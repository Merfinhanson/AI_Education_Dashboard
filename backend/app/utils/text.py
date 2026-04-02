import hashlib
import json
import math
import re
from collections import Counter
from itertools import pairwise


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_identifier(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"[^A-Za-z0-9]", "", value).upper()


def tokenize(text: str) -> list[str]:
    normalized = normalize_whitespace(text).lower()
    tokens = re.findall(r"[a-z0-9']+", normalized)
    return [token for token in tokens if token not in STOPWORDS]


def keyword_candidates(text: str, limit: int = 6) -> list[str]:
    counts = Counter(tokenize(text))
    return [token for token, _ in counts.most_common(limit)]


def cosine_overlap(text_a: str, text_b: str) -> float:
    vector_a = Counter(tokenize(text_a))
    vector_b = Counter(tokenize(text_b))
    if not vector_a or not vector_b:
        return 0.0

    intersection = set(vector_a) & set(vector_b)
    numerator = sum(vector_a[token] * vector_b[token] for token in intersection)
    denominator = math.sqrt(sum(value * value for value in vector_a.values())) * math.sqrt(
        sum(value * value for value in vector_b.values())
    )
    return numerator / denominator if denominator else 0.0


def sentence_split(text: str) -> list[str]:
    candidates = re.split(r"(?<=[.!?])\s+|\n+", text or "")
    return [normalize_whitespace(candidate) for candidate in candidates if normalize_whitespace(candidate)]


def coverage_against_points(answer_text: str, points: list[str]) -> list[tuple[str, float]]:
    answer_units = sentence_split(answer_text) or [answer_text]
    results: list[tuple[str, float]] = []
    for point in points:
        best = max(cosine_overlap(point, answer_unit) for answer_unit in answer_units)
        results.append((point, round(best, 4)))
    return results


def stable_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True)


def load_json_list(value: str | None) -> list:
    if not value:
        return []
    parsed = json.loads(value)
    return parsed if isinstance(parsed, list) else []


def order_similarity(order_a: list[str], order_b: list[str]) -> float:
    if not order_a or not order_b:
        return 0.0
    if order_a == order_b:
        return 1.0

    pairs_a = set(pairwise(order_a))
    pairs_b = set(pairwise(order_b))
    if not pairs_a or not pairs_b:
        overlap = len(set(order_a) & set(order_b))
        return overlap / max(len(set(order_a) | set(order_b)), 1)

    return len(pairs_a & pairs_b) / len(pairs_a | pairs_b)
