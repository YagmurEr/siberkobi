from __future__ import annotations

AI_BOTS = ("GPTBot", "OAI-SearchBot", "Googlebot", "Bingbot")


def _parse_robots_groups(text: str) -> list[dict]:
    groups: list[dict] = []
    agents: list[str] = []
    rules: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal agents, rules
        if agents:
            groups.append({"agents": agents[:], "rules": rules[:]})
        agents = []
        rules = []

    for raw in (text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        key = key.lower()
        if key == "user-agent":
            if rules:
                flush()
            agents.append(value.lower())
        elif key in {"allow", "disallow"} and agents:
            rules.append((key, value))
    flush()
    return groups


def _root_access(groups: list[dict], bot: str) -> dict:
    bot_key = bot.lower()
    specific = [g for g in groups if bot_key in g["agents"]]
    applicable = specific or [g for g in groups if "*" in g["agents"]]
    if not applicable:
        return {"status": "allowed", "reason": "Bot için özel engel tanımlı değil."}

    rules = [rule for group in applicable for rule in group["rules"]]
    if any(kind == "allow" and path == "/" for kind, path in rules):
        return {"status": "allowed", "reason": "robots.txt kök yol için Allow: / içeriyor."}
    if any(kind == "disallow" and path == "/" for kind, path in rules):
        return {"status": "blocked", "reason": "robots.txt kök yol için Disallow: / içeriyor."}
    return {"status": "allowed", "reason": "Kök yolu engelleyen bir Disallow: / kuralı bulunmadı."}


def evaluate_ai_visibility(
    robots: dict,
    *,
    json_ld_count: int,
    h1_count: int,
    h2_count: int,
    paragraph_count: int,
    semantic_tags: list[str],
) -> dict:
    groups = _parse_robots_groups(robots.get("text", "")) if robots.get("ok") else []
    bots: dict[str, dict] = {}

    for bot in AI_BOTS:
        if not robots.get("ok"):
            bots[bot] = {
                "status": "unknown",
                "reason": "robots.txt erişilemediği için erişim durumu doğrulanamadı.",
            }
        else:
            bots[bot] = _root_access(groups, bot)

    checks = {
        "robots_accessible": bool(robots.get("ok")),
        "oai_searchbot_allowed": bots["OAI-SearchBot"]["status"] == "allowed",
        "gptbot_allowed": bots["GPTBot"]["status"] == "allowed",
        "googlebot_allowed": bots["Googlebot"]["status"] == "allowed",
        "bingbot_allowed": bots["Bingbot"]["status"] == "allowed",
        "json_ld": json_ld_count > 0,
        "single_h1": h1_count == 1,
        "has_h2": h2_count > 0,
        "paragraphs": paragraph_count >= 2,
        "semantic_structure": bool(semantic_tags),
    }
    score = sum(1 for value in checks.values() if value)

    if score >= 8:
        status = "Uygun"
    elif score >= 5:
        status = "Kısmen Uygun"
    else:
        status = "Geliştirilmeli"

    return {
        "status": status,
        "score": score,
        "maximum": len(checks),
        "bots": bots,
        "checks": checks,
        "json_ld_count": json_ld_count,
        "content": {
            "h1_count": h1_count,
            "h2_count": h2_count,
            "paragraph_count": paragraph_count,
            "semantic_tags": semantic_tags,
            "readable": checks["single_h1"] and checks["paragraphs"],
        },
        "scope_note": (
            "Bu ücretsiz kontrol robots.txt kök-yol erişimi, indirilen statik HTML, temel başlık-paragraf "
            "yapısı ve JSON-LD varlığı üzerinden deterministik olarak yapılır. JavaScript ile sonradan "
            "oluşan içerik, WAF/CDN bot engelleri ve gerçek bot erişimi bu kontrolde doğrulanmaz."
        ),
    }
