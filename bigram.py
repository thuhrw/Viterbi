import json
from typing import Dict
import os
import sys
import io
import jieba
from pypinyin import lazy_pinyin
from tqdm import tqdm

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import time


def save_to_json(data, file_path):
    """通用保存JSON文件的函数"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"数据已保存到: {file_path}")


def is_chinese_char(character):
    """检查是否是汉字"""
    if "\u4e00" <= character and character <= "\u9fff":
        return True
    return False


def is_chinese_word(string):
    "检查是否是纯中文词"
    for i in range(len(string)):
        if is_chinese_char(string[i]):
            continue
        else:
            return False
    return True


def remove_prefix(text):
    """去除'原标题：'"""
    prefix = "原标题："
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def get_pinyin():
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


def char_process1(path: str):
    """处理一元字的个数和概率"""
    char_count = {}
    for filename in tqdm(os.listdir(path)):
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
    freq = {}
    for character, count in char_count.items():
        freq[character] = count / total_count

    return char_count, freq


def char_process2(path: str, cnt1):
    """处理二元字的个数与概率"""
    pair_count = {}
    for filename in tqdm(os.listdir(path)):
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

    freq = {}
    for pair, cnt in pair_count.items():
        character1, character2 = pair.split()
        freq[pair] = cnt / cnt1[character1]

    return pair_count, freq


def word_process1(path: str):
    """处理一元词的个数和概率"""
    word_count = {}
    for filename in tqdm(os.listdir(path)):
        if filename == "README.txt":
            continue
        with open(os.path.join(path, filename), "r", encoding="gbk") as f:
            for line in f:
                line = line.strip()
                line = json.loads(line)
                text1 = remove_prefix(line["html"])
                text2 = line["title"]
                text1_list = jieba.lcut(text1)
                text2_list = jieba.lcut(text2)
                for word in text1_list:
                    if not is_chinese_word(word):
                        continue
                    if word not in word_count:
                        word_count[word] = 0
                    word_count[word] += 1
                for word in text2_list:
                    if not is_chinese_word(word):
                        continue
                    if word not in word_count:
                        word_count[word] = 0
                    word_count[word] += 1
    total_count = sum(word_count.values())
    freq1 = {}
    for word, count in word_count.items():
        freq1[word] = count / total_count

    zhuyin = {}
    for word in word_count:
        pinylist = lazy_pinyin(word)
        piny = pinylist[0]
        for i in range(1, len(pinylist)):
            piny += " " + pinylist[i]
        if piny not in zhuyin:
            zhuyin[piny] = []
        zhuyin[piny].append(word)

    return word_count, freq1, zhuyin


def word_process2(path: str, cnt1):
    """处理二元词的个数与概率"""
    pair_count = {}
    for filename in tqdm(os.listdir(path)):
        if filename == "README.txt":
            continue
        with open(os.path.join(path, filename), "r", encoding="gbk") as f:
            for line in f:
                line = line.strip()
                line = json.loads(line)
                text1 = remove_prefix(line["html"])
                text2 = line["title"]
                text1_list = jieba.lcut(text1)
                text2_list = jieba.lcut(text2)
                for i in range(len(text1_list) - 1):
                    word1 = text1_list[i]
                    word2 = text1_list[i + 1]
                    if is_chinese_word(word1) and is_chinese_word(word2):
                        pair = word1 + " " + word2
                        if pair not in pair_count:
                            pair_count[pair] = 0
                        pair_count[pair] += 1
                for i in range(len(text2_list) - 1):
                    word1 = text2_list[i]
                    word2 = text2_list[i + 1]
                    if is_chinese_word(word1) and is_chinese_word(word2):
                        pair = word1 + " " + word2
                        if pair not in pair_count:
                            pair_count[pair] = 0
                        pair_count[pair] += 1
    freq2 = {}
    for pair, cnt in pair_count.items():
        word1, word2 = pair.split()
        freq2[pair] = cnt / cnt1[word1]

    return pair_count, freq2


class Node:
    def __init__(self, character, prob=0.0, prev=None):
        self.character = character
        self.prob = prob
        self.prev = prev


delta = 1e-10


def viterbi(
    pinyin_sequence,
    dictionary,
    char_freq1,
    char_freq2,
    char_cnt1,
    char_cnt2,
    word_freq1,
    word_freq2,
    word_cnt1,
    word_cnt2,
    zhuyin,
):
    """viterbi算法实现"""
    global delta
    pinyin_sequence = pinyin_sequence.strip().split()
    length = len(pinyin_sequence)
    dps = []
    for i in range(0, 50):
        dps.append([])
    max_word_length = 4

    # init
    append_cnt = 0
    for i in range(0, min(max_word_length, length)):
        word_pinyin = pinyin_sequence[0]
        if i >= 1:
            for j in range(1, i):
                word_pinyin += " " + pinyin_sequence[j]

        if word_pinyin in zhuyin:
            for item in zhuyin[word_pinyin]:
                dps[len(item) - 1].append(Node(item, word_freq1[item], None))
                append_cnt += 1
    if append_cnt == 0:
        for word in dictionary.get(pinyin_sequence[0]):
            if word in char_freq1.keys():
                dps[0].append(Node(word, char_freq1[word], None))

    # next
    for idx in range(1, length):
        append_cnt = 0
        for i in range(0, min(max_word_length, (length - idx))):
            word_pinyin = pinyin_sequence[idx]
            if i >= 1:
                for j in range(1, i + 1):
                    word_pinyin += " " + pinyin_sequence[idx + j]

            if word_pinyin in zhuyin:
                for character2 in zhuyin[word_pinyin]:
                    max_prob = -1e10
                    prev_node = None
                    for node in dps[idx - 1]:
                        character1 = node.character
                        query = character1 + " " + character2
                        if query in word_freq2:
                            prob = node.prob * word_freq2[query]
                            if prob > max_prob:
                                max_prob = prob
                                prev_node = node
                        else:
                            prob = node.prob * delta
                            if prob > max_prob:
                                max_prob = prob
                                prev_node = node

                    dps[idx + len(character2) - 1].append(
                        Node(character2, max_prob, prev_node)
                    )
                    append_cnt += 1

        if append_cnt == 0:
            for character2 in dictionary.get(pinyin_sequence[idx]):
                if character2 not in char_freq1:
                    continue
                max_prob = -1e10
                prev_node = None
                for node in dps[idx - 1]:
                    character1 = node.character[-1]
                    query = character1 + " " + character2
                    if query in char_freq2:
                        prob = node.prob * char_freq2[query]
                        if prob > max_prob:
                            max_prob = prob
                            prev_node = node
                    else:
                        prob = node.prob * delta
                        if prob > max_prob:
                            max_prob = prob
                            prev_node = node
                dps[idx].append(
                    Node(
                        character2,
                        max_prob,
                        prev_node,
                    )
                )
    ans_node = None
    max_prob = -1e10
    tail = 49
    while dps[tail] == []:
        tail -= 1
    for node in dps[tail]:
        if node.prob > max_prob:
            max_prob = node.prob
            ans_node = node

    ans = []
    while ans_node is not None:
        ans.append(ans_node.character)
        ans_node = ans_node.prev
    ansstr = ""
    for item in reversed(ans):
        ansstr += item
    return ansstr


def main():
    corpus_folder_path = "./corpus/sina_news_gbk"
    start = time.time()
    dictionary = get_pinyin()

    char_cnt1, char_freq1 = char_process1(corpus_folder_path)

    char_cnt2, char_freq2 = char_process2(corpus_folder_path, char_cnt1)

    word_cnt1, word_freq1, zhuyin = word_process1(corpus_folder_path)

    word_cnt2, word_freq2 = word_process2(corpus_folder_path, word_cnt1)

    end = time.time()
    elapsed = end - start
    print(f"初始化耗时：{elapsed:.2f} 秒")

    save_to_json(dictionary, "./saved_data/pinyin_char_dict.json")
    save_to_json(char_cnt1, "./saved_data/char_count.json")
    save_to_json(char_freq1, "./saved_data/char_frequency.json")
    save_to_json(char_cnt2, "./saved_data/char_pair_count.json")
    save_to_json(char_freq2, "./saved_data/char_pair_frequency.json")
    save_to_json(word_cnt1, "./saved_data/word_count.json")
    save_to_json(word_freq1, "./saved_data/word_frequency.json")
    save_to_json(zhuyin, "./saved_data/pinyin_word_dict.json")
    save_to_json(word_cnt2, "./saved_data/word_pair_count.json")
    save_to_json(word_freq2, "./saved_data/word_pair_frequency.json")

    # data_path = "./saved_data/"
    # # 1. 拼音-汉字字典
    # with open(data_path + "pinyin_char_dict.json", "r", encoding="utf-8") as f:
    #     dictionary = json.load(f)

    # # 2. 一元字
    # with open(data_path + "char_count.json", "r", encoding="utf-8") as f:
    #     char_cnt1 = json.load(f)
    # with open(data_path + "char_frequency.json", "r", encoding="utf-8") as f:
    #     char_freq1 = json.load(f)

    # # 3. 二元字
    # with open(data_path + "char_pair_count.json", "r", encoding="utf-8") as f:
    #     char_cnt2 = json.load(f)
    # with open(data_path + "char_pair_frequency.json", "r", encoding="utf-8") as f:
    #     char_freq2 = json.load(f)

    # # 4. 一元词
    # with open(data_path + "word_count.json", "r", encoding="utf-8") as f:
    #     word_cnt1 = json.load(f)
    # with open(data_path + "word_frequency.json", "r", encoding="utf-8") as f:
    #     word_freq1 = json.load(f)

    # # 5. 拼音-词语映射
    # with open(data_path + "pinyin_word_dict.json", "r", encoding="utf-8") as f:
    #     zhuyin = json.load(f)

    # # 6. 二元词
    # with open(data_path + "word_pair_count.json", "r", encoding="utf-8") as f:
    #     word_cnt2 = json.load(f)
    # with open(data_path + "word_pair_frequency.json", "r", encoding="utf-8") as f:
    #     word_freq2 = json.load(f)

    start = time.time()
    for idx, pinyin_sequence in enumerate(sys.stdin):
        ans = viterbi(
            pinyin_sequence,
            dictionary,
            char_freq1,
            char_freq2,
            char_cnt1,
            char_cnt2,
            word_freq1,
            word_freq2,
            word_cnt1,
            word_cnt2,
            zhuyin,
        )
        print(ans)
    end = time.time()
    elapsed = end - start
    print(f"测试耗时：{elapsed:.2f} 秒")


if __name__ == "__main__":
    main()

# 1483.36
# 3.93
