# —*— coding: utf-8 —*—
# —*— coding: utf-8 —*—
# @Time:    2020/2/14 22:09
# @Author:  syoryu
# @File:    强智教务系统获取校历.py
# @Software:PyCharm
from bs4 import BeautifulSoup
import re


def schoolCalender(text):
    soup = BeautifulSoup(text, 'lxml')
    page = soup.findAll("tr", {"height": "28"})
    list = []  #
    list_tmp = []  #
    for i in page:
        for j in i.findAll("td", {"title": True}):
            tmp = re.split('年|月', j.attrs['title'])
            tmp = [int(x) for x in tmp]
            list_tmp.append(tmp)
    for index in range(0, len(list_tmp), 7):
        list.append(list_tmp[index:index + 7])

    school_weeks = []
    for i in range(len(list)):
        school_weeks.append(i + 1)

    return list, school_weeks
