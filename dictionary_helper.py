import json
import re

def load_dictionary(path="resources/words_dictionary.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {word.lower(): freq for word, freq in data.items()}

def find_matches(partial_word, dictionary, max_matches=3):
    regex = "^" + partial_word.lower().replace("_", ".") + "$"
    pattern = re.compile(regex)
    matches = [word for word in dictionary if pattern.match(word)]
    matches.sort(key=lambda w: dictionary[w], reverse=True)
    return [word.upper() for word in matches[:max_matches]]

def extract_suggestions(partial_text, dictionary, max_matches=3):
    text = partial_text.replace(" ", "").upper()
    suggestions = []
    max_len = 12
    seen = set()

    for i in range(len(text)):
        for l in range(3, max_len + 1):
            frag = text[i:i + l]
            if len(frag) < l or "_" not in frag or not frag.replace("_", "").isalpha():
                continue
            if frag in seen:
                continue
            seen.add(frag)

            matches = find_matches(frag, dictionary, max_matches)
            if matches:
                suggestion_lines = [match for match in matches]
                suggestions.append(f"单词 {frag} 可匹配：" + "，".join(suggestion_lines))
    return suggestions
