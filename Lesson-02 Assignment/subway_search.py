#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
from collections.abc import Iterable
from collections import defaultdict
import collections
import math
import requests
from urllib import parse
import networkx as nx
from bs4 import *
import re
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def flatten(lst):  # 嵌套list拉平
    for item in lst:
        if isinstance(item, collections.Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            yield item


class crawl_subway_geo:
    def __init__(self):
        self.key = "e86595afe8494e43ac6252b6330636d0"


    def get_url_by_gaode(self,address):
        url = "https://restapi.amap.com/v3/geocode/geo"
        params = {"key": self.key,
                  "address": address,
                  "city": "北京"}
        return url, params


    def get_location_by_gaode(self,address):
        url, params = self.get_url_by_gaode(address)
        response = requests.get(url, params).json()
        if response["status"] == "1" and len(response["geocodes"]) != 0:
            for item in response['geocodes']:
                location = item["location"].split(",")
                longitude = location[0]
                latitude = location[1]
                return longitude, latitude
        else:
            return "", ""
    def main(self,line_stations):
        with open("beijing_subway_geo.txt", "w", encoding="utf-8") as beijing_subway_geo_file:
            stations = list(flatten(list(line_stations.values())))
            for name in stations:
                long,lati = self.get_location_by_gaode(name)
                if name and long and lati:
                    beijing_subway_geo_file.write("{}:{},{}\n".format(name, long,lati))




class crawl_subway_line:
    def __init__(self):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
                     " Chrome/75.0.3770.142 Safari/537.36"
        self.headers = {'user-agent': user_agent}


    def get_request_soup(self,url):
        page = requests.get(url, headers=self.headers, allow_redirects=False)
        soup = BeautifulSoup(page.content, 'html.parser', from_encoding='utf-8')
        return soup

    def get_line_url(self):
        url_init = "https://baike.baidu.com/item/%E5%8C%97%E4%BA%AC%E5%9C%B0%E9%93%81/408485"
        init_soup = self.get_request_soup(url_init)
        line_url = dict()
        for line in init_soup.find_all("table")[2].find_all("a")[:-1]:
            line_url[line.get_text().strip()] = "https://baike.baidu.com{}".format(line.get("href").strip())
        return line_url

    def get_line_station(self):
        station_re = re.compile(r"车站列表|车站信息|车站名称")
        station_name_re = re.compile(r"站")
        station_info_dict = defaultdict(list)
        lines_url = self.get_line_url()

        for line_name,url in lines_url.items():
            line_soup = self.get_request_soup(url)
            if line_name == "北京地铁16号线":
                for i, l in enumerate(line_soup.find_all("table")):
                    th_str = " ".join([item.get_text() for item in l.find_all("th")])
                    if th_str and station_re.findall(th_str):
                        a_slice = l.find_all("a")
                        for s in a_slice:
                            s_str = s.get_text()
                            if station_name_re.findall(s_str):
                                station_info_dict[line_name].append(s_str)
                        break
            else:
                for i, l in enumerate(line_soup.find_all("table")):
                    if l.caption and station_re.findall(l.caption.get_text()):
                        for s in l.find_all("a"):
                            s_str = s.get_text()
                            if station_name_re.findall(s_str):
                                station_info_dict[line_name].append(s_str)
                        break
                    elif l.b and station_re.findall(l.b.get_text()):
                        a_slice = l.find_all("a")
                        for s in l.find_all("a"):
                            s_str = s.get_text()
                            if station_name_re.findall(s_str):
                                station_info_dict[line_name].append(s_str)
                        break
        return station_info_dict

    def clean_station(self):
        """清洗站名，把（出站）等非地点站名清洗掉"""
        get_re = re.compile(r"(?P<station>[A-Za-z0-9\u4e00-\u9fa5]+).*")
        del_re = re.compile(r"站台")
        line_station = self.get_line_station()
        line_station_clean = defaultdict(list)
        for name,station_list in line_station.items():
            station_clean = []
            station_clean_temp = list(map(lambda x:get_re.match(x).group("station"),station_list))
            assert len(station_list) == len(station_clean_temp)
            for s in station_clean_temp:
                if not del_re.findall(s):
                    if s[-1] == "站":
                        s_new = s[:-1] + "地铁站"
                    else:
                        s_new = s + "地铁站"
                    line_station_clean[name].append(s_new)
        return line_station_clean

    def main(self):
        with open("beijing_subway_line.txt", "w",encoding="utf-8") as beijing_subway_line_file:
            beijing_subway_line = self.clean_station()
            for title, line in beijing_subway_line.items():
                beijing_subway_line_file.write("{}:{}\n".format(title, ",".join(line)))
        return beijing_subway_line




class search_subway_line:
    def __init__(self):
        path_subway_line = "beijing_subway_line_true.txt"
        path_subway_geo = "beijing_subway_geo_true.txt"
        self.subway_line = self.load_line_data(path_subway_line)
        self.subway_geo = self.load_geo_data(path_subway_geo)
    def load_line_data(self,path):
        subway_line = dict()
        with open(path, "r", encoding="utf-8") as beijing_subway_line_fin:
            for line in beijing_subway_line_fin.readlines():
                name, stations = line.strip().split(":")
                if name.strip() and stations.strip():
                    subway_line[name.strip()] = [item.strip() for item in stations.strip().split(",")]
        return subway_line
    def load_geo_data(self,path):
        subway_geo = dict()
        with open(path, "r", encoding="utf-8") as beijing_subway_geo_fin:
            for line in beijing_subway_geo_fin.readlines():
                station, location = line.strip().split(":")
                if station.strip() and location.strip():
                    subway_geo[station.strip()] = list(map(lambda x: float(x), location.strip().split(",")))
        return subway_geo

    def get_station_connection(self):
        station_connection = defaultdict(list)
        for line_name, line_stat in self.subway_line.items():
            for idx, stat in enumerate(line_stat):
                if idx == 0:
                    station_connection[stat].append(line_stat[idx + 1])
                elif idx == len(line_stat) - 1:
                    station_connection[stat].append(line_stat[idx - 1])
                else:
                    station_connection[stat].extend([line_stat[idx - 1], line_stat[idx + 1]])
        for stat, stat_adja in station_connection.items():
            station_connection[stat] = list(set(stat_adja))
        return station_connection

    def plt_subway_lines(self):
        station_connection = self.get_station_connection()
        # nx.draw(city_with_road, city_location, with_labels=True, node_size=30)
        nx.draw(nx.Graph(station_connection), self.subway_geo, with_labels=False, node_size=3,
                node_color='red', edge_color='blue', font_size=9)
        plt.show()

    def geo_distance(self,origin, destination):
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371  # km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c
        return d

    def get_geo_distance(self,city1, city2):
        return self.geo_distance(self.subway_geo[city1], self.subway_geo[city2])

    def get_line_distance(self,station_line):
        d = 0
        for idx,item in enumerate(station_line[:-1]):
            d += self.get_geo_distance(station_line[idx],station_line[idx+1])
        return d

    def search(self,start,destination,sort_candidate):
        station_connection = self.get_station_connection()
        pathes = [[start]]
        visited = set()
        while pathes:
            path = pathes.pop()
            frontier = path[-1]
            if frontier in visited: continue
            successors = station_connection[frontier]
            for city in successors:
                if city in visited: continue
                new_path = path + [city]
                pathes = [new_path] + pathes
                # pathes.append(new_path)
                if city == destination :
                    return new_path
            visited.add(frontier)
            if sort_candidate == "minimum_transfer_priority":
                pathes = self.minimum_transfer_priority(pathes)
            elif sort_candidate == "shortest_path_priority":
                pathes = self.shortest_path_priority(pathes)


    def shortest_path_priority(self,pathes):
        return sorted(pathes, key=self.get_line_distance, reverse=True)
    def minimum_transfer_priority(self,pathes):
        return sorted(pathes,key =len,reverse=True)

    def search_by_way(self,start,destination,by_way,sort_candidate):
        station_connection = self.get_station_connection()
        pathes = [[start]]
        visited = set()
        while pathes:
            path = pathes.pop()
            frontier = path[-1]
            if frontier in visited: continue
            successors = station_connection[frontier]
            for city in successors:
                if city in visited: continue
                new_path = path + [city]
                # pathes = [new_path] + pathes
                pathes.append(new_path)

                flag = sum([1 if item in new_path else 0 for item in by_way ])
                # print(flag)
                if city == destination and flag == len(by_way):
                    return new_path
            visited.add(frontier)
            if sort_candidate == "minimum_transfer_priority":
                pathes = self.minimum_transfer_priority(pathes)
            elif sort_candidate == "shortest_path_priority":
                pathes = self.shortest_path_priority(pathes)







if __name__ == '__main__':
    """  作业：Finish the search problem"""
    #爬取地铁线路
    # subway_line =  crawl_subway_line()
    # line_stations = subway_line.main()

    #爬取站点坐标
    # subway_geo = crawl_subway_geo()
    # subway_geo.main(line_stations)

    # 搜索策略
    search_line = search_subway_line()
    # search_line.plt_subway_lines()    #画地铁线路图
    # serch_line = search_line.search("奥体中心","天安门东","shortest_path_priority")
    search_line_by_way = search_line.search_by_way("奥体中心","天安门东",["安华桥","东四"],"shortest_path_priority")
    print(search_line_by_way)  #绕远路线做不到过路




    #获取

    pass