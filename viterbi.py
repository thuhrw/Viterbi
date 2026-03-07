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
    cnt1 = {}
    for pinyin, item in word1.items():
        count_list = item["counts"]
        total_count = sum(count_list)
        if pinyin not in freq1:
            freq1[pinyin] = {}

        for idx, character in enumerate(item["words"]):
            freq1[pinyin][character] = count_list[idx] / total_count
            if character not in cnt1:
                cnt1[character] = 0
            cnt1[character] = count_list[idx]
    return freq1, cnt1


def process_word2(word2: Dict, cnt1: Dict):
    """处理二元词频表,得到转移概率"""
    freq2 = {}
    for pinyin_pair, item in word2.items():
        count_list = item["counts"]
        for idx, word in enumerate(item["words"]):
            character1, character2 = word.split(" ")
            if word not in freq2:
                freq2[word] = 0.0
            freq2[word] = count_list[idx] / cnt1[character1]
    return freq2


class Node:
    def __init__(self, character, prob=0.0, probaccu=0.0, prev=None):
        self.character = character
        self.prob = prob
        self.probaccu = probaccu
        self.prev = prev


delta = 1e-4


def viterbi(pinyin_sequence, freq1, freq2):
    """viterbi算法实现"""
    pinyin_sequence = pinyin_sequence.strip().split()
    # 二维数组
    dps = []
    dp_init = []
    for word in freq1[pinyin_sequence[0]]:
        dp_init.append(
            Node(
                word,
                freq1[pinyin_sequence[0]][word],
                freq1[pinyin_sequence[0]][word],
                None,
            )
        )
    dps.append(dp_init)
    for i in range(1, len(pinyin_sequence)):
        dp = []
        for character2 in freq1[pinyin_sequence[i]]:
            max_prob = 0.0
            prev_node = None
            for node in dps[i - 1]:
                character1 = node.character
                query = character1 + " " + character2
                if query in freq2:
                    probaccu = node.probaccu * freq2[query]
                    if probaccu > max_prob:
                        max_prob = probaccu
                        prev_node = node
                    
                else:
                    probaccu = node.probaccu * delta / cnt1[character1]
                    if probaccu > max_prob:
                        max_prob = probaccu
                        prev_node = node
                    
            dp.append(
                Node(
                    character2,
                    freq1[pinyin_sequence[i]][character2],
                    max_prob,
                    prev_node,
                )
            )
        dps.append(dp)

    ans_node = None
    max_prob = 0.0
    for node in dps[-1]:
        if node.probaccu > max_prob:
            max_prob = node.probaccu
            ans_node = node
        elif node.probaccu == max_prob:
            if node.prob > ans_node.prob:
                ans_node = node

    ans = []
    while ans_node is not None:
        ans.append(ans_node.character)
        ans_node = ans_node.prev
    ans.reverse()
    return "".join(ans)


if __name__ == "__main__":
    word1 = read_onefreq()
    word2 = read_twofreq()
    freq1, cnt1 = process_word1(word1)
    freq2 = process_word2(word2, cnt1)
    # print(freq1)
    # print(freq2)
    try:
        while True:
            pinyin_sequence = input()
            ans = viterbi(pinyin_sequence, freq1, freq2)
            print(ans)
    except EOFError:
        pass
