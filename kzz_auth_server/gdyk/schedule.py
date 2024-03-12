# —*— coding: utf-8 —*—
# @Time:    2023/2/14 22:09
# @Author:  syoryu
# @File:    强智教务系统获取课程表.py
# @Software:PyCharm
import re
from bs4 import BeautifulSoup
import numpy as np
from bs4.element import NavigableString

def schedule(text):
    soup = BeautifulSoup(text, 'lxml')
    page = soup.find_all('div', attrs={'class': "kbcontent"})
    page = page[::2]

    teachers1, teachers2 = [], []
    weeks1, weeks2 = [], []
    classrooms1, classrooms2 = [], []
    for i in page:
        teachers1.append(i.find('font', attrs={'title': '老师'}))
        weeks1.append(i.find('font', attrs={'title': '周次(节次)'}))
        classrooms1.append(i.find('font', attrs={'title': '教室'}))

    my_detail = list(page)

    for i in teachers1:
        if i == None:
            teachers2.append('\n')
        else:
            teachers2.append(i.string)
    for i in weeks1:
        if i == None:
            weeks2.append('\n')
        else:
            weeks2.append(i.string)
    for i in classrooms1:
        if i == None:
            classrooms2.append('\n')
        else:
            classrooms2.append(i.string)

    all_data = []  # 所有课程数组
    # 一个课程暂存数组
    temp = {
        'idx': None,  # index
        'course_name': None,  # 课程名
        'class_place': None,  # 课室
        'teacher': None,  # 教师
        'weeks': None,  # 周次
        'weekday': None,  # 周几
        'color': None,  # 颜色
        'weeks_desc':{
            'start' : None,
            'last': None,
            'weeks':None
        }
    }
    none = [None, None, None, None, None, None,{None, None, None}]  # 统一置空
    segregate = {}  # 分割字典
    index = 0  # 课程编号
    # print(len(my_detail))
    tmp_res = my_detail
    for i in range(len(my_detail)):
        if my_detail[i].text != '\xa0':
            if ("---------" in my_detail[i].text):
                segregate[i] = index
            if (classrooms2[i] == '\n'):
                # continue
                classrooms2[i] = "无教室"
            temp['idx'] = index
            if isinstance(my_detail[i].contents[2], NavigableString):  # 如果课程名字太长他会变成两行,两个NavigableString，分别在位置0和2
                course_name_tmp = my_detail[i].contents[0] + my_detail[i].contents[2]
            else:
                course_name_tmp = my_detail[i].contents[0]
            temp['course_name'] = course_name_tmp  # 课程名字
            temp['class_place'] = classrooms2[i]  # 课室
            temp['teacher'] = teachers2[i]  # 教师
            temp['weeks'] = weeks2[i] + ''  # 周次+节次
            temp['weekday'] = i % 7 + 1  # 周几
            temp['color'] = index  # 颜色
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))  # 置空
            index = index + 1
    # 处理同一个框内多个课程
    for i in segregate.keys():
        tmp = my_detail[i].contents
        a = np.array(tmp,dtype=object)
        eq_letter = np.where(a == "---------------------")
        cut_point = eq_letter[0]
        if(len(cut_point) == 1):
            # 第二节课
            tmp_list = tmp[cut_point[0]:]
            temp = lineOrNot(tmp_list, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
        elif len(cut_point) == 2:
            # 第二节课
            tmp_list1 = tmp[cut_point[0]:cut_point[1]]
            temp = lineOrNot(tmp_list1, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
            # 第三节课
            tmp_list2 = tmp[cut_point[1]:]
            temp = lineOrNot(tmp_list2, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
        elif len(cut_point) == 3:
            # 第二节课
            tmp_list1 = tmp[cut_point[0]:cut_point[1]]
            temp = lineOrNot(tmp_list1, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
            # 第三节课
            tmp_list2 = tmp[cut_point[1]:cut_point[2]]
            temp = lineOrNot(tmp_list2, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
            # 第四节课
            tmp_list2 = tmp[cut_point[2]:]
            temp = lineOrNot(tmp_list2, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
        elif len(cut_point) == 4:
            # 第二节课
            tmp_list1 = tmp[cut_point[0]:cut_point[1]]
            temp = lineOrNot(tmp_list1, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
            # 第三节课
            tmp_list2 = tmp[cut_point[1]:cut_point[2]]
            temp = lineOrNot(tmp_list2, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
            # 第四节课
            tmp_list3 = tmp[cut_point[2]:cut_point[3]]
            temp = lineOrNot(tmp_list3, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1
            # 第五节课
            tmp_list4 = tmp[cut_point[3]:]
            temp = lineOrNot(tmp_list4, i, index)
            all_data.append(temp)
            temp = dict(zip(temp.keys(), none))
            index = index + 1

    # 底部备注课程,idx:999
    page2 = soup.find('td', attrs={'colspan': "7"})
    if(page2!=None):
        remarks = page2.text.split((';'))
        all_data.append({'idx': 999, 'remarks': remarks[0:len(remarks) - 1]})
    else:
        all_data.append({'idx': 999, 'remarks': []})

    # 解析week -> weeks_desc
    all_data = weeks_parse(all_data)
    # print('课表', all_data)
    return all_data

# 判断是网课还是线下课，返回一个课程对象
def lineOrNot(data, i, index):
    # 一个课程暂存数组
    temp = {
        'idx': None,  # index
        'course_name': None,  # 课程名
        'class_place': None,  # 课室
        'teacher': None,  # 教师
        'weeks': None,  # 周次
        'weekday': None,  # 周几
        'color': None,  # 颜色
        'weeks_desc': {
            'start': None,
            'last': None,
            'weeks': None
        }
    }

    temp['idx'] = index
    if isinstance(data[4], NavigableString):
        temp['course_name'] = data[2] + data[4]
    else:
        temp['course_name'] = data[2]
    temp['class_place'] = '无教室'
    temp['teacher'] = '无教师'
    temp['weeks'] = ''
    temp['weekday'] = i % 7 + 1
    temp['color'] = index

    for item in data:
        if not isinstance(item, NavigableString):
            if len(item.attrs) == 1:
                if item.attrs['title'] == "老师":
                    temp['teacher'] = item.contents[0]
                elif item.attrs['title'] == "周次(节次)":
                    temp['weeks'] = item.contents[0]
                elif item.attrs['title'] == "教室":
                    temp['class_place'] = item.contents[0]
    return temp

# 解析weeks -> weeks_desc:start,last,weeks ,,并且去除地点为== '\n'的课程
def weeks_parse(data):
    all_data = data
    for i in range(len(all_data) - 1):
        # if all_data[i]['class_place'] == '\n':
        #     continue
        weeks_range = all_data[i]['weeks'].split('(周)')[0] #.split('-')
        tmp = []
        tmp_2 = []
        start = 0
        last = 0
        tmp_2 = dealWeeksdesc(weeks_range)
        if weeks_range != '':
            # start:9,last:2 -> 第9节上课，持续2节
            section_range = all_data[i]['weeks'].split('[')[1].split('节')[0].split('-')
            section_range = [int(x) for x in section_range]

            start = min(section_range)
            last = max(section_range) - min(section_range) + 1
            all_data[i]['weeks_desc'] = {'start': start, 'last': last, 'weeks': tmp_2}
    # 同课程同颜色
    tmp_course = []
    for i in all_data:
        tmp_course.append(i.get('course_name'))
    for j in all_data:
        j['color'] = tmp_course.index(j.get('course_name'))
    return all_data

def dealWeeksdesc(weeks_range):
    tmp = []
    tmp_2 = []
    if(weeks_range != ''):
        if (',' in weeks_range):  # weeks_range.__contains__(',')
            weeks_range = weeks_range.split(',')
            for i in range(len(weeks_range)):
                tmp = weeks_range[i].split('-')
                tmp = [int(x) for x in tmp]
                for j in range(min(tmp), max(tmp) + 1):
                    tmp_2.append(j)
        elif len(weeks_range) == 1:
            tmp_2.append(int(weeks_range[0]))
        else:
            weeks_range = weeks_range.split('-')
            tmp = [int(x) for x in weeks_range]
            for j in range(min(tmp), max(tmp) + 1):
                tmp_2.append(j)
    return tmp_2