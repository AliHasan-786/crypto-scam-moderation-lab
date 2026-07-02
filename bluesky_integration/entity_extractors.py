from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ExtractedEntity:
    entity_type: str
    value: str
    raw: str
    source: str
    risk_weight: float

    def to_dict(self) -> dict:
        return asdict(self)


SHORTENER_DOMAINS = {
    "bit.ly",
    "buff.ly",
    "cutt.ly",
    "is.gd",
    "lnkd.in",
    "ow.ly",
    "rebrand.ly",
    "shorturl.at",
    "t.co",
    "tiny.cc",
    "tinyurl.com",
}

RISKY_TLDS = {
    "best",
    "cash",
    "click",
    "icu",
    "link",
    "mom",
    "quest",
    "rest",
    "shop",
    "top",
    "win",
    "xyz",
    "zip",
}

BRAND_PATTERNS = (
    ("bitcoin", r"\b(?:bitcoin|btc)\b", 0.18),
    ("ethereum", r"\b(?:ethereum|eth)\b", 0.18),
    ("solana", r"\b(?:solana|sol)\b", 0.16),
    ("tether", r"\b(?:tether|usdt)\b", 0.14),
    ("coinbase", r"\bcoinbase\b", 0.22),
    ("binance", r"\bbinance\b", 0.22),
    ("metamask", r"\bmeta\s*mask\b|\bmetamask\b", 0.24),
    ("trust_wallet", r"\btrust\s+wallet\b", 0.24),
    ("ledger", r"\bledger\b", 0.2),
    ("tesla", r"\btesla\b", 0.18),
    ("elon_musk", r"\belon\s+musk\b|\bmusk\b", 0.2),
    ("microsoft", r"\bmicrosoft\b", 0.16),
)

RISK_PHRASE_PATTERNS = (
    ("connect_wallet", r"\bconnect(?:ing)?\s+(?:your\s+)?wallet\b", 0.9),
    ("verify_wallet", r"\bverif(?:y|ied|ication)\s+(?:your\s+)?wallet\b", 0.86),
    ("wallet_drainer", r"\bwallet\s+drain(?:er|ing)?\b", 0.88),
    ("seed_phrase", r"\bseed\s+phrase\b|\brecovery\s+phrase\b", 0.92),
    ("private_key", r"\bprivate\s+key\b", 0.92),
    ("send_crypto", r"\bsend\s+(?:[0-9.]+\s*)?(?:btc|bitcoin|eth|ethereum|sol|usdt|crypto|tokens?)\b", 0.82),
    ("guaranteed_returns", r"\bguaranteed\s+returns?\b|\brisk[-\s]?free\s+profits?\b", 0.78),
    ("double_your_money", r"\bdouble\s+(?:your\s+)?(?:money|btc|eth|crypto)\b", 0.82),
    ("airdrop_claim", r"\bairdrop\b|\bclaim\s+(?:free\s+)?(?:btc|eth|crypto|tokens?|reward)\b", 0.76),
    ("processing_fee", r"\bprocessing\s+fee\b|\bupfront\s+fee\b|\brelease\s+fee\b", 0.74),
    ("recovery_service", r"\brecovery\s+service\b|\bfunds?\s+recover(?:y|ed)\b", 0.7),
    ("limited_time", r"\blimited\s+time\b|\bwindow\s+closes\b|\bfinal\s+warning\b|\bact\s+now\b", 0.68),
    ("official_giveaway", r"\bofficial\s+(?:airdrop|giveaway|reward|event)\b", 0.74),
    ("private_trading_group", r"\bprivate\s+trading\s+group\b|\bvip\s+(?:crypto\s+)?signals?\b", 0.68),
)

DOMAIN_RE = re.compile(
    r"\b(?:https?://)?(?:www\.)?"
    r"([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+)"
    r"(?:/[^\s<>()\"']*)?",
    re.IGNORECASE,
)
HANDLE_RE = re.compile(r"(?<!\w)@([a-z0-9][a-z0-9.-]{2,80})(?!\w)", re.IGNORECASE)
ETHEREUM_RE = re.compile(r"\b0x[a-fA-F0-9]{20,64}\b")
BITCOIN_RE = re.compile(r"\b(?:bc1[ac-hj-np-z02-9]{25,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b")
SOLANA_RE = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")


def entity_id(entity_type: str, value: str) -> str:
    digest = hashlib.sha256(f"{entity_type}:{value}".encode("utf-8")).hexdigest()
    return digest[:24]


def normalize_obfuscation(text: str) -> str:
    normalized = str(text or "")
    normalized = re.sub(r"\bhxxps://", "https://", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bhxxp://", "http://", normalized, flags=re.IGNORECASE)
    normalized = re.sub(
        r"\s*(?:\[|\(|\{)\s*(?:\.|dot)\s*(?:\]|\)|\})\s*",
        ".",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(r"\s+dot\s+", ".", normalized, flags=re.IGNORECASE)
    return normalized


def clean_domain(candidate: str) -> str:
    value = candidate.strip().strip(".,;:!?)('\"").lower()
    parsed = urlparse(value if "://" in value else f"http://{value}")
    domain = (parsed.netloc or parsed.path).split("@")[-1].split(":")[0]
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.strip(".")


def domain_risk_weight(domain: str) -> float:
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    if domain in SHORTENER_DOMAINS:
        return 0.76
    if tld in RISKY_TLDS:
        return 0.58
    if any(token in domain for token in ("airdrop", "giveaway", "claim", "secure", "verify", "reward")):
        return 0.62
    return 0.25


def add_entity(
    entities: dict[tuple[str, str], ExtractedEntity],
    entity_type: str,
    value: str,
    raw: str,
    source: str,
    risk_weight: float,
) -> None:
    normalized_value = str(value or "").strip().lower()
    if not normalized_value:
        return
    key = (entity_type, normalized_value)
    candidate = ExtractedEntity(
        entity_type=entity_type,
        value=normalized_value,
        raw=str(raw or value).strip(),
        source=source,
        risk_weight=round(float(risk_weight), 3),
    )
    existing = entities.get(key)
    if existing is None or candidate.risk_weight > existing.risk_weight:
        entities[key] = candidate


def extract_domains(text: str, entities: dict[tuple[str, str], ExtractedEntity]) -> None:
    normalized = normalize_obfuscation(text)
    for match in DOMAIN_RE.finditer(normalized):
        if match.start() > 0 and normalized[match.start() - 1] == "@":
            continue
        raw = match.group(0)
        domain = clean_domain(raw)
        if "." not in domain or len(domain) > 253:
            continue
        risk_weight = domain_risk_weight(domain)
        add_entity(entities, "domain", domain, raw, "text", risk_weight)
        if domain in SHORTENER_DOMAINS:
            add_entity(entities, "url_shortener", domain, raw, "text", 0.82)


def extract_wallets(text: str, entities: dict[tuple[str, str], ExtractedEntity]) -> None:
    normalized = normalize_obfuscation(text)
    lower = normalized.lower()
    for match in ETHEREUM_RE.finditer(normalized):
        add_entity(entities, "wallet", match.group(0).lower(), match.group(0), "ethereum_address", 0.92)
    for match in BITCOIN_RE.finditer(normalized):
        add_entity(entities, "wallet", match.group(0), match.group(0), "bitcoin_address", 0.9)
    if any(term in lower for term in ("wallet", "address", "deposit", "send ", "airdrop", "claim")):
        for match in SOLANA_RE.finditer(normalized):
            add_entity(entities, "wallet", match.group(0), match.group(0), "wallet_like_string", 0.72)


def extract_handles(
    text: str,
    entities: dict[tuple[str, str], ExtractedEntity],
    *,
    author_handle: str | None = None,
    author_did: str | None = None,
    author_display_name: str | None = None,
) -> None:
    for match in HANDLE_RE.finditer(text):
        add_entity(entities, "handle", match.group(1), match.group(0), "mention", 0.28)
    if author_handle:
        add_entity(entities, "actor", author_handle, author_handle, "author_handle", 0.2)
    if author_did:
        add_entity(entities, "actor", author_did, author_did, "author_did", 0.2)
    if author_display_name:
        display = str(author_display_name).strip()
        if 2 <= len(display) <= 80:
            add_entity(entities, "display_name", display, display, "author_display_name", 0.12)


def extract_brands(text: str, entities: dict[tuple[str, str], ExtractedEntity]) -> None:
    for value, pattern, risk_weight in BRAND_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            add_entity(entities, "brand", value, match.group(0), "brand_mention", risk_weight)


def extract_risk_phrases(text: str, entities: dict[tuple[str, str], ExtractedEntity]) -> None:
    normalized = normalize_obfuscation(text)
    for value, pattern, risk_weight in RISK_PHRASE_PATTERNS:
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if match:
            add_entity(entities, "risk_phrase", value, match.group(0), "policy_phrase", risk_weight)


def extract_entities(
    text: str,
    *,
    author_handle: str | None = None,
    author_did: str | None = None,
    author_display_name: str | None = None,
) -> list[ExtractedEntity]:
    entities: dict[tuple[str, str], ExtractedEntity] = {}
    text = str(text or "")
    extract_domains(text, entities)
    extract_wallets(text, entities)
    extract_handles(
        text,
        entities,
        author_handle=author_handle,
        author_did=author_did,
        author_display_name=author_display_name,
    )
    extract_brands(text, entities)
    extract_risk_phrases(text, entities)
    return sorted(entities.values(), key=lambda item: (item.entity_type, item.value))
