from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse


SUSPICIOUS_TLDS = {"cash", "click", "io", "net", "top", "xyz"}
SHORTENER_DOMAINS = {"bit.ly", "cutt.ly", "is.gd", "lnkd.in", "shorturl.at", "t.co", "tinyurl.com"}
CAMPAIGN_KEYWORDS = {
    "airdrop",
    "bonus",
    "claim",
    "crypto",
    "giveaway",
    "login",
    "prize",
    "secure",
    "support",
    "verify",
    "wallet",
    "winner",
}
BRAND_TERMS = {
    "binance",
    "blackrock",
    "coinbase",
    "ethereum",
    "metamask",
    "microsoft",
    "opensea",
    "solana",
    "tesla",
    "uniswap",
}
KNOWN_OFFICIAL_DOMAINS = {
    "binance.com",
    "blackrock.com",
    "coinbase.com",
    "ethereum.org",
    "metamask.io",
    "microsoft.com",
    "opensea.io",
    "solana.com",
    "tesla.com",
    "uniswap.org",
}

DOMAIN_PATTERN = re.compile(
    r"\b(?:https?://)?(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:[a-z]{2,24})\b(?:/[^\s]*)?",
    re.IGNORECASE,
)


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_url_surface(text: object) -> str:
    value = strip_accents(str(text or ""))
    value = re.sub(r"hxxps?://", "https://", value, flags=re.IGNORECASE)
    value = re.sub(r"\[\.\]|\(\.\)|\{\.\}", ".", value)
    value = re.sub(r"\s+(?:dot|\[dot\]|\(dot\))\s+", ".", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def domain_for_url(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"http://{value}")
    domain = parsed.netloc.lower()
    return domain[4:] if domain.startswith("www.") else domain


def tld_for_domain(domain: str) -> str:
    pieces = domain.rsplit(".", 1)
    return pieces[1] if len(pieces) == 2 else ""


def risk_factors_for_url(*, raw_text: str, normalized_url: str, domain: str) -> list[str]:
    lower_text = raw_text.lower()
    lower_url = normalized_url.lower()
    tld = tld_for_domain(domain)
    factors: list[str] = []

    if re.search(r"hxxps?://|\[\.\]|\(\.\)|\{\.\}|\s+dot\s+", raw_text, re.IGNORECASE):
        factors.append("defanged_url")
    if domain in SHORTENER_DOMAINS:
        factors.append("url_shortener")
    if tld in SUSPICIOUS_TLDS:
        factors.append("suspicious_tld")
    if any(keyword in domain for keyword in CAMPAIGN_KEYWORDS):
        factors.append("campaign_keyword_domain")
    if any(keyword in lower_url for keyword in ("airdrop", "claim", "connect", "verify", "wallet")):
        factors.append("wallet_or_claim_path")
    if any(brand in domain for brand in BRAND_TERMS) and domain not in KNOWN_OFFICIAL_DOMAINS:
        factors.append("brand_impersonation_domain")
    if "qr code" in lower_text or "image ocr" in lower_text or "source account not visible" in lower_text:
        factors.append("missing_source_or_ocr_context")

    return sorted(set(factors))


def risk_weight(factors: list[str]) -> float:
    weights = {
        "brand_impersonation_domain": 0.30,
        "campaign_keyword_domain": 0.18,
        "defanged_url": 0.14,
        "missing_source_or_ocr_context": 0.16,
        "suspicious_tld": 0.12,
        "url_shortener": 0.16,
        "wallet_or_claim_path": 0.18,
    }
    return min(1.0, sum(weights.get(factor, 0.05) for factor in factors))


def analyze_text_urls(text: object) -> dict[str, object]:
    raw_text = str(text or "")
    normalized_surface = normalize_url_surface(raw_text)
    urls = []
    seen = set()

    for match in DOMAIN_PATTERN.finditer(normalized_surface):
        normalized_url = match.group(0).rstrip(".,;:!?)\"]}")
        domain = domain_for_url(normalized_url)
        if not domain or domain in seen:
            continue
        seen.add(domain)
        factors = risk_factors_for_url(raw_text=raw_text, normalized_url=normalized_url, domain=domain)
        urls.append(
            {
                "normalizedUrl": normalized_url,
                "domain": domain,
                "tld": tld_for_domain(domain),
                "riskFactors": factors,
                "riskWeight": risk_weight(factors),
            }
        )

    urls.sort(key=lambda item: item["riskWeight"], reverse=True)
    highest_risk = urls[0]["riskWeight"] if urls else 0.0
    factor_counts: dict[str, int] = {}
    for item in urls:
        for factor in item["riskFactors"]:
            factor_counts[factor] = factor_counts.get(factor, 0) + 1

    return {
        "normalizedSurface": normalized_surface,
        "urlCount": len(urls),
        "highestRisk": highest_risk,
        "factorCounts": dict(sorted(factor_counts.items())),
        "urls": urls,
    }
