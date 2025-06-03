import json
from collections import Counter

def analyze_frequency(text):
    """
    统计文本中每个字母的频率，并返回按频率排序的列表
    """
    text = text.upper()
    letters = [c for c in text if c.isalpha()]
    total = len(letters)
    freq = Counter(letters)

    return {char: round((count / total) * 100, 2) for char, count in freq.items()}


def suggest_key(cipher_freq_dict):
    """
    根据英文字母频率排序，推测密钥置换表。
    返回：密文字母 -> 英文高频字母 映射建议
    """
    # 读取英文标准频率
    with open("resources/english_freq.json", "r") as f:
        standard_freq = json.load(f)

    # 按频率排序
    cipher_sorted = sorted(cipher_freq_dict.items(), key=lambda x: x[1], reverse=True)
    english_sorted = sorted(standard_freq.items(), key=lambda x: x[1], reverse=True)

    # 构造映射建议
    suggestions = {}
    for (ciph_letter, _), (eng_letter, _) in zip(cipher_sorted, english_sorted):
        suggestions[ciph_letter] = eng_letter

    return suggestions
