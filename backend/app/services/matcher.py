import re
from rapidfuzz import fuzz

STOP = {"and","or","the","of","in","for","to","with","a","an","is","are","as","on","by","from","will","be"}

def tokens(text: str):
    return {t.lower() for t in re.findall(r"[A-Za-z0-9+#.]+", text or "") if len(t) > 1 and t.lower() not in STOP}

def match_score(profile_text: str, job_text: str) -> tuple[int, list[str], list[str]]:
    p = tokens(profile_text)
    j = tokens(job_text)
    if not j:
        return 0, [], []
    overlap = sorted(p & j)
    missing = sorted(list(j - p))[:15]
    keyword_score = int(min(100, (len(overlap) / max(8, min(len(j), 45))) * 100))
    fuzzy_score = fuzz.partial_ratio(profile_text.lower(), job_text.lower())
    score = int((keyword_score * 0.7) + (fuzzy_score * 0.3))
    return min(score, 100), overlap[:20], missing
