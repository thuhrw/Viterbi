import json
from typing import Dict


def read_onefreq():
    """读取一元词频表"""
    with open("./1_word.txt", "r", encoding="utf-8") as f:
        return json.loads(f.read())


def read_twofreq():
    """读取二元词频表"""
    with open("./2_word.txt", "r", encoding="utf-8") as f:
        return json.loads(f.read())


def process_word1(word1: Dict):
    """处理一元词频表,得到初始概率"""
    freq1 = {}
    for pinyin, item in word1.items():
        count_list = item["counts"]
        total_count = sum(count_list)
        for idx, character in enumerate(item["words"]):
            freq1[character] = count_list[idx] / total_count
    return freq1


def process_word2(word2: Dict):
    """处理二元词频表,得到转移概率"""
    freq2 = {}
    for pinyin_pair, item in word2.items():
        count_list = item["counts"]
        temp = {}
        for idx, character_pair in enumerate(item["words"]):
            character1, character2 = character_pair.split(" ")
            if character1 not in temp:
                temp[character1] = {}
            temp[character1][character2] = count_list[idx]

        # 计算转移概率
        prob = {}
        for character1, item in temp.items():
            if character1 not in prob:
                prob[character1] = {}
            total = sum(item.values())
            for character2, count in item.items():
                prob[character1][character2] = count / total

        freq2[pinyin_pair] = prob
    return freq2


if __name__ == "__main__":
    word1 = read_onefreq()
    word2 = read_twofreq()
    freq1 = process_word1(word1)
    freq2 = process_word2(word2)
    print(json.dumps(freq1, ensure_ascii=False))
    print(json.dumps(freq2, ensure_ascii=False))
