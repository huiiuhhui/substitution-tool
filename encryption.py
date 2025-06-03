def encrypt(text, key_mapping):
    """
    将明文 text 使用给定的 key_mapping（26字母置换）加密。
    """
    text = text.upper()
    result = ""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    mapping = {alphabet[i]: key_mapping[i] for i in range(26)}

    for char in text:
        if char in mapping:
            result += mapping[char]
        else:
            result += char  # 保留标点、空格、数字
    return result


def decrypt(ciphertext, key_mapping):
    """
    使用 key_mapping 的反向映射解密 ciphertext。
    """
    ciphertext = ciphertext.upper()
    result = ""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    reverse_mapping = {key_mapping[i]: alphabet[i] for i in range(26)}

    for char in ciphertext:
        if char in reverse_mapping:
            result += reverse_mapping[char]
        else:
            result += char
    return result
