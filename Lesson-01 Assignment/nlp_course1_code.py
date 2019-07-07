#!/usr/bin/env python
# -*- coding:utf-8 –*-

import random
import pandas as pd
import re
import jieba
from collections import Counter
from functools import reduce
from operator import add,mul
import matplotlib.pyplot as plt
import numpy as np

#random.choice 随机选择

def adj():
    return random.choice("蓝色的|好看的|小小的".split("|")).split()[0]
def adj_star():
    return random.choice([None, adj() + adj()])

simple_grammar = """
sentence => noun_phrase verb_phrase
noun_phrase => Article Adj* noun
Adj* => null | Adj Adj*
verb_phrase => verb noun_phrase
Article =>  一个 | 这个
noun =>   女人 |  篮球 | 桌子 | 小猫
verb => 看着   |  坐在 |  听着 | 看见
Adj =>  蓝色的 | 好看的 | 小小的
"""
#在西部世界里，一个”人类“的语言可以定义为：

human = """
human = 自己 寻找 活动
自己 = 我 | 俺 | 我们 
寻找 = 找找 | 想找点 
活动 = 乐子 | 玩的
"""

#一个“接待员”的语言可以定义为
host = """
host = 寒暄 报数 询问 业务相关 结尾 
报数 = 我是 数字 号 ,
数字 = 单个数字 | 数字 单个数字 
单个数字 = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 
寒暄 = 称谓 打招呼 | 打招呼
称谓 = 人称 ,
人称 = 先生 | 女士 | 小朋友
打招呼 = 你好 | 您好 
询问 = 请问你要 | 您需要
业务相关 = 玩玩 具体业务
玩玩 = null
具体业务 = 喝酒 | 打牌 | 打猎 | 赌博
结尾 = 吗？
"""

programming = """
stmt => if_exp | while_exp | assignment 
assignment => var = var
if_exp => if ( var ) { /n .... stmt }
while_exp=> while ( var ) { /n .... stmt }
var => chars number
chars => char | char char
char => student | name | info  | database | course
number => 1 | 2 | 3
"""

def create_grammar(grammar_str,split="=>",line_split="\n"):
    """
    function:解析自定义语法
    :param grammar_str: 自定义语法 字符串
    :param split: 表达式分隔符
    :param line_split: 换行分隔符
    :return: 语法字典
    """
    grammar = {}
    for line in grammar_str.split(line_split):
        if not line.strip():continue
        exp,stmt = line.split(split)
        grammar[exp.strip()] =  [s.split()for s in stmt.split("|")]
    return grammar

choice = random.choice
def generate(gram,target):
    """
    function:生成句子
    :param gram: dict,语法
    :param target: 生成语言的主体
    :return: str,生成句
    """
    if target not in gram: return target
    expanded = [generate(gram,s) for s in choice(gram[target])]
    return " ".join(e if e != "/n" else "\n" for e in expanded if e != "null")

sentence = generate(gram=create_grammar(simple_grammar),target="sentence")
print(sentence)
for i in range(20):
    print(generate(create_grammar(host,split="="),"host"))
print(generate(gram=create_grammar(programming,split='=>'),target = "stmt"))


filename = "D:/PycharmPrograms/NLP_course/data/sqlResult_1558435.csv"
news_content = pd.read_csv(filename,encoding="gb18030")
articles = news_content["content"].tolist()
print(articles[110])
def tokens(string):
    return re.findall("\w+",string)
with_jieba_cut = Counter(jieba.cut(articles[110]))
articles_clean = ["".join(tokens(str(s)))for s in articles]
print(articles_clean[0])
# with open('article_9k.txt', 'w') as f:
#     for a in articles_clean:
#         f.write(a + '\n')

def cut(string):
    """
    functioin:结巴切词
    :param string: 字符串
    :return: 分词后的list
    """
    return list(jieba.cut(string))
TOKEN = []
for i,line in enumerate(open("../data/article_9k.txt").readlines()):
    if i % 100 == 0:print(i)
    if i > 10000:break
    TOKEN += cut(line)
words_count = Counter(TOKEN)

frequences = [f for w,f in words_count.most_common(100)]
x = [i for i in range(100)]
plt.plot(x,frequences)
plt.show()
plt.plot(x,np.log(frequences))
plt.show()
articles_words = [cut(string) for string in articles_clean[:10000]]
TOKENS = reduce(add,articles_words)
print(TOKENS)
# matplotlib inline
def prob_1(word):
    return words_count[word]/len(TOKEN)

TOKEN =[str(t) for t in TOKEN]
TOKEN_2_GRAM = ["".join(TOKEN[i:i+2]) for i in range(len(TOKEN[:-2]))]
word_count_2 = Counter(TOKEN_2_GRAM)
def prob_2(word1,word2):
    if word1 + word2 in word_count_2:return word_count_2[word1+word2] / len(TOKEN_2_GRAM)
    else:
        return 1 / len(TOKEN_2_GRAM)
print(prob_2("时代性","人物"))
def get_probabilty(sentence):
    words = cut(sentence)
    sentence_pro = 1
    for i ,word in enumerate(words[:-1]):
        next_ = words[i+1]
        probability = prob_2(word,next_)
        sentence_pro *= probability
    return sentence_pro
for sen in [generate(gram=create_grammar(simple_grammar),target="sentence") for i in range(10)]:
    print("sentence:{} with Pro: {}".format(sen,get_probabilty(sen)))

need_compared = [
    "今天晚上请你吃大餐，我们一起吃日料 明天晚上请你吃大餐，我们一起吃苹果",
    "真事一只好看的小猫 真是一只好看的小猫",
    "今晚我去吃火锅 今晚火锅去吃我",
    "洋葱奶昔来一杯 养乐多绿来一杯"
]
for s in need_compared:
    s1,s2 = s.split()
    p1,p2  = get_probabilty(s1),get_probabilty(s2)
    better = s1 if p1 > p2 else s2
    print( "{} is more possible".format(better))
    print("-"*4 + "{} with probability {}".format(s1,p1))
    print("-" * 4 + "{} with probability {}".format(s2, p2))
