#!/usr/bin/env python
# -*- coding:utf-8 –*-
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import numpy as np
from gensim.models.word2vec import LineSentence
import os
from gensim.models import Word2Vec
import jieba
import re
import logging
from langconv import *
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import codecs
def softmax(vec):
    """
    softmax函数
    :param vec: 向量
    :return:
    """
    vec -= np.max(vec)  #vec-np.max(vec)
    exp = np.exp(vec)
    return exp / np.sum(exp)


def train_word2vec_model(cut_corpus_path,word2vec_model_path,word2vec_txt_path,size=200):
    """
    训练word2vec模型
    :param cut_corpus_path: 切割好的语料路径
    :param word2vec_model_path: 模型存储路径
    :param word2vec_txt_path: 词向量存储文档 txt
    :param size: 词向量维度 默认200
    :return: 模型和词向量文档
    """
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sentences = LineSentence(cut_corpus_path)  # 加载语料
    model = Word2Vec(sentences, size=size)  # 训练
    model.save(word2vec_model_path)  # 保存模型
    model.wv.save_word2vec_format(word2vec_txt_path, binary=False)


def tsne_plot(model,stop_words,thred=1000):
    """
    word2vec可视化
    :param model: word2vec模型
    :return:
    """
    words = []
    vecs = []
    count = 0
    for word in model.wv.vocab:
        if word not in stop_words:
            if count > thred:break
            vecs.append(model[word])
            words.append(word)
            count += 1
    #perplexity 浮点型，数据量越大，数值越大
    #n_components：嵌入式空间的维度
    #n_iter：int 优化最大迭代次数
    #init 嵌入的初始化

    tsne_model = TSNE(perplexity=40,n_components=2,
                      init="pca",n_iter=5000,random_state=23)

    new_values = tsne_model.fit_transform(vecs)
    x = []
    y = []

    for v in new_values:
        x.append(v[0])
        y.append(v[1])


    plt.figure(figsize = (100,100))
    for i in range(len(x)):
        plt.scatter(x[i],y[i])
        # print(i)
        # print(x[i],y[i])
        # plt.annotate(word[i],xy=(x[i],y[i]),textcoords="offset points",ha="right",va="bottom")
    plt.show()


def build_word2vec_corpus(raw_corpus_path,vecs):
    """
    清洗wiki的原始数据
    :param raw_corpus_path: 数据路径
    :return: 清洗后的语料
    """
    del_re = re.compile(r"<.*doc.*>|/(/)|（）")
    fout = codecs.open(cut_corpus_path,"w","utf-8")
    with codecs.open(wiki_extracted_corpus_path, 'r', 'utf-8') as myfile:
        for line in myfile:
            line = re.sub(del_re,"",line).strip()
            if not line:continue
            words_list = list(jieba.cut(Converter('zh-hans').convert(line)))
            fout.write(" ".join(words_list) + "\n")
    fout.close()


def open_txtFile(inputFile):
    """
    function:打开文本文件，txt格式，输出成list(每一个元素去除“/n")
    author：DS
    :param inputFile: 待打开的txt文件路径，str
    :return: list,每一个元素是原来txt文件的每一行（去除“/n”），元素非空
    """
    with open(inputFile,"r",encoding="utf-8") as fin:
        lines_ = fin.readlines()
    lines = [item.strip() for item in lines_ if len(item.strip())>0]
    return lines


if __name__ == '__main__':
    # """=================== softmax复写==================="""
    a = np.array([1,2,3,4,5])
    a_softmax = softmax(a)
    # ""=================== Assignment-04 基于维基百科的词向量构建"=================== "
    # Step-01: Download Wikipedia Chinese Corpus ：
    root = "D:\BaiduNetdiskDownload\维基百科中文20190720"
    wiki_corpus_name = "zhwiki-20190720-pages-articles-multistream.xml.bz2"
    wiki_corpus_path = os.path.join(root,wiki_corpus_name)
    # print(wiki_corpus_path)

    # Step-02: Using https://github.com/attardi/wikiextractor to extract the wikipedia corpus
    # python wikiExtractor.py -b 1024M -o extracted wiki_corpus_name
    wiki_extracted_corpus_path = "D:/Code/wikiextractor-master/extracted/wiki_all.txt"
    wiki_cut_corpus_path = "data/word2vec_cut_corpus.txt"
    # build_word2vec_corpus(wiki_extracted_corpus_path, wiki_cut_corpus_path)

    # Step-03: Using gensim get word vectors
    word2vec_model_path =  "data/word2vec.model"
    # train_word2vec_model(wiki_cut_corpus_path,word2vec_model_path, "data/word2vec.txt")

    # Step-04: Using some words to test your preformance.
    word2vec_model = Word2Vec.load(word2vec_model_path)
    # print(word2vec_model.most_similar("温暖"))
    # print("~~~~~~~~~~~")
    # print(word2vec_model.most_similar("啤酒"))


    # Step-05: Using visualization tools
    # with open("data/stop_words.txt","r","utf-8") as fin:
    #     lines = fin.readlines()
    stop_words = open_txtFile("data/stop_words.txt")
    tsne_plot(word2vec_model,stop_words)





