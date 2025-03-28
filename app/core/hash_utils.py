# app/core/hash_utils.py

def hamming_distance(hash1: str, hash2: str) -> int:
    """
    두 이진 문자열 간 해밍 거리 계산
    """
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
