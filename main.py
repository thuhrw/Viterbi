import json
from typing import Dict
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import time


def is_chinese_char(character):
    """检查是否是汉字"""
    if "\u4e00" <= character and character <= "\u9fff":
        return True
    return False


def remove_prefix(text):
    """去除'原标题：'"""
    prefix = "原标题："
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def pinyin():
    """字典"""
    dictionary = {}
    with open("./data/拼音汉字表.txt", "r", encoding="gbk") as f:
        for line in f:
            line = line.strip().split()
            pinyin = line[0]
            dictionary[pinyin] = []
            for character in line[1:]:
                dictionary[pinyin].append(character)
    return dictionary


def word_process1(path: str):
    """处理一元字的个数和概率"""
    char_count = {}
    for filename in os.listdir(path):
        if filename == "README.txt":
            continue
        with open(os.path.join(path, filename), "r", encoding="gbk") as f:
            for line in f:
                line = line.strip()
                line = json.loads(line)
                text = remove_prefix(line["html"]) + line["title"]
                for character in text:
                    if is_chinese_char(character):
                        if character not in char_count:
                            char_count[character] = 0
                        char_count[character] += 1

    total_count = sum(char_count.values())
    freq1 = {}
    for character, count in char_count.items():
        freq1[character] = count / total_count

    return char_count, freq1


def word_process2(path: str, cnt1):
    """处理二元字的个数与概率"""
    pair_count = {}
    for filename in os.listdir(path):
        if filename == "README.txt":
            continue
        with open(os.path.join(path, filename), "r", encoding="gbk") as f:
            for line in f:
                line = line.strip()
                line = json.loads(line)
                text1 = remove_prefix(line["html"])
                text2 = line["title"]
                for i in range(len(text1) - 1):
                    character1 = text1[i]
                    character2 = text1[i + 1]
                    if is_chinese_char(character1) and is_chinese_char(character2):
                        pair = character1 + " " + character2
                        if pair not in pair_count:
                            pair_count[pair] = 0
                        pair_count[pair] += 1
                for i in range(len(text2) - 1):
                    character1 = text2[i]
                    character2 = text2[i + 1]
                    if is_chinese_char(character1) and is_chinese_char(character2):
                        pair = character1 + " " + character2
                        if pair not in pair_count:
                            pair_count[pair] = 0
                        pair_count[pair] += 1

    freq2 = {}
    for pair, cnt in pair_count.items():
        character1, character2 = pair.split()
        freq2[pair] = cnt / cnt1[character1]

    return pair_count, freq2


class Node:
    def __init__(self, character, prob=0.0, probaccu=0.0, prev=None):
        self.character = character
        self.prob = prob  # 单字的概率，冗余设计，但是懒于删除了
        self.probaccu = probaccu  # 从起点到当前节点的累计概率
        self.prev = prev


delta = 1e-10  # 自定义的平滑参数，避免概率为0导致的乘积为0问题
# m = 0.87


def viterbi(pinyin_sequence, dictionary, freq1, freq2, cnt1):
    """viterbi算法实现"""
    global delta
    pinyin_sequence = pinyin_sequence.strip().split()
    dps = []
    dp_init = []
    if pinyin_sequence[0] not in dictionary:
        return None
    for word in dictionary.get(pinyin_sequence[0]):
        if word in freq1.keys():
            dp_init.append(
                Node(
                    word,
                    freq1[word],
                    freq1[word],
                    None,
                )
            )

    dps.append(dp_init)
    # 初始化

    for i in range(1, len(pinyin_sequence)):
        dp = []
        if pinyin_sequence[i] not in dictionary:
            return None
        for character2 in dictionary.get(pinyin_sequence[i]):
            if character2 not in freq1:
                continue
            max_prob = -1e10
            prev_node = None
            for node in dps[i - 1]:
                character1 = node.character
                query = character1 + " " + character2
                if query in freq2:
                    # probaccu = node.probaccu * (m * freq2[query] +(1-m) * freq1[character2])
                    probaccu = node.probaccu * freq2[query]
                    if probaccu > max_prob:
                        max_prob = probaccu
                        prev_node = node

                else:
                    probaccu = node.probaccu * delta
                    if probaccu > max_prob:
                        max_prob = probaccu
                        prev_node = node
            dp.append(
                Node(
                    character2,
                    freq1[character2],
                    max_prob,
                    prev_node,
                )
            )
        dps.append(dp)

    # 回溯，寻找整体概率最大的序列
    ans_node = None
    max_prob = -1e10
    for node in dps[-1]:
        if node.probaccu > max_prob:
            max_prob = node.probaccu
            ans_node = node

    ans = []
    while ans_node is not None:
        ans.append(ans_node.character)
        ans_node = ans_node.prev
    ans.reverse()
    return "".join(ans)


def main():
    # start = time.time()
    dictionary = pinyin()
    corpus_folder_path = "./corpus/sina_news_gbk"
    cnt1, freq1 = word_process1(corpus_folder_path)
    # temp_saving_path = "./word_cnt1.json"
    # with open(temp_saving_path, "w", encoding="utf-8") as f:
    #     json.dump(cnt1, f, ensure_ascii=False, indent=4)
    # temp_saving_path = "./word_freq1.json"
    # with open(temp_saving_path, "w", encoding="utf-8") as f:
    #     json.dump(freq1, f, ensure_ascii=False, indent=4)
    cnt2, freq2 = word_process2(corpus_folder_path, cnt1)
    # temp_saving_path = "./word_cnt2.json"
    # with open(temp_saving_path, "w", encoding="utf-8") as f:
    #     json.dump(cnt2, f, ensure_ascii=False, indent=4)
    # temp_saving_path = "./word_freq2.json"
    # with open(temp_saving_path, "w", encoding="utf-8") as f:
    #     json.dump(freq2, f, ensure_ascii=False, indent=4)

    # end = time.time()
    # elapsed= end - start
    # print(f"初始化耗时：{elapsed:.2f} 秒")

    # with open("./word_freq1.json", "r", encoding="utf-8") as f:
    #     freq1 = json.load(f)
    # with open("./word_freq2.json", "r", encoding="utf-8") as f:
    #     freq2 = json.load(f)
    # with open("./word_cnt1.json", "r", encoding="utf-8") as f:
    #     cnt1 = json.load(f)
    # with open("./word_cnt2.json", "r", encoding="utf-8") as f:
    #     cnt2 = json.load(f)
    # start = time.time()
    for idx, pinyin_sequence in enumerate(sys.stdin):
        ans = viterbi(pinyin_sequence, dictionary, freq1, freq2, cnt1)
        print(ans)
    # end = time.time()
    # elapsed = end - start
    # print(f"测试耗时：{elapsed:.2f} 秒")


if __name__ == "__main__":
    main()
