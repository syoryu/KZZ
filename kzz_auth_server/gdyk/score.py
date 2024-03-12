# —*— coding: utf-8 —*—
# @Time:    2020/2/14 22:09
# @Author:  syoryu
# @File:    强智教务系统获取成绩.py
# @Software:PyCharm
import requests
import ddddocr
import os
import re
from bs4 import BeautifulSoup
from lxml import etree
from gdyk.recognize import recognize


def getScore(username, password, xnxq01id):
    username = username  # 账号
    password = password  # 密码
    xnxq01id = xnxq01id  # 查询学期
    session = get_cookie()  # 获取session
    verify_code = get_verify_code(session)  # 获取验证码
    encoded = get_code(username, password, session)  # 加密算法
    statusCode = login(encoded, verify_code, session)  # 登录
    if statusCode == '2002':
        score = get_score(xnxq01id, session)  # 获取成绩
        return score, '2002'
    elif statusCode == '4002':
        return [], '4002'


# 获取成绩
def get_score(xnxq01id, session):
    host = 'https://jw.educationgroup.cn/gzasc_jsxsd/kscj/cjcx_list'
    data = {
        'kksj': xnxq01id,  # 查询学期
        'kcxz': '',
        'kcmc': '',
        'xsfs': 'all'
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '101',
        'Host': 'jw.educationgroup.cn',
        'Referer': 'https://jw.educationgroup.cn/gzasc_jsxsd/kscj/cjcx_query',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'}
    response = session.post(host, headers=headers, data=data)
    return parse_score(response.text)  # 解析成绩


def parse_score(text):
    soup = BeautifulSoup(text, 'lxml')
    title = soup.findAll('th', {'class': 'Nsb_r_list_thb'})
    table = soup.find('table', {'id': 'dataList'})
    content = table.findAll('td')

    scoreList = []

    tmp_2 = []
    for i in range(int(len(content) / 16)):
        tmp = []
        for j in range(16):
            tmp.append(content[i * 16 + j].text)
        tmp_2.append(tmp)

    for i in tmp_2:
        parse_score = i[5].replace('\r', '').replace('\n', '').replace('\t', '')
        score = {'idx': i[0], 'semester': i[1], 'course_id': i[2], 'course_name': i[3], 'group_name': i[4],
                 'course_score': parse_score, 'score_tag': i[6], 'course_credit': i[7], 'course_hours': i[8],
                 'course_point': i[9], 'rebuilt_semester': i[10], 'assess_mode': i[11], 'exam_attrs': i[12],
                 'course_attrs': i[13], 'course_prop': i[14], 'gcourse_category': i[15]}
        scoreList.append(score)
    # print('解析成绩', soup)
    # print('获取到成绩页面', text)
    # pattern = r'所修门数:(\d+)\s*所修总学分:(\d+)\s*平均学分绩点:(\d+\.\d+)\s*平均成绩:(\d+\.\d+)'
    # text = "所修门数:88\s*"
    match = re.search(r"所修门数:([\d.]+)\s*", text)
    if match:
        course_num = match.group(1)
    else:
        course_num = "未获取到"

    match = re.search(r"所修总学分:([\d.]+)\s*", text)
    if match:
        total_credit = match.group(1)
    else:
        total_credit = "未获取到"

    match = re.search(r"平均学分绩点:([\d.]+)\s*", text)
    if match:
        average_gpa = match.group(1)
    else:
        average_gpa = "未获取到"

    match = re.search(r"平均成绩:([\d.]+)\s*", text)
    if match:
        average_score = match.group(1)
    else:
        average_score = "未获取到"


    # match = re.search(pattern, text)
    # print('🐎🐎🐎🐎🐎', match)
    # scoreAppend = {
    #     "course_num" : match.group(1),
    #     "total_credit" : match.group(2),
    #     "average_gpa" : match.group(3),
    #     "average_score" : match.group(4),
    # }
    scoreAppend = {
        "course_num": course_num,
        "total_credit": total_credit,
        "average_gpa": average_gpa,
        "average_score": average_score,
    }

    print('🐎🐎🐎🐎🐎', scoreAppend)
    score = {
        "scoreList": scoreList,
        "scoreAppend": scoreAppend
    }
    return score


# 获取session
def get_cookie():
    host = 'https://jw.educationgroup.cn/gzasc/'
    session = requests.session()
    session.get(host, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'
    })
    # print('session参数:', session.cookies)
    return session


# 加密算法
def get_code(username, password, session):
    str_url = 'https://jw.educationgroup.cn/gzasc/Logon.do?method=logon&flag=sess'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'jw.educationgroup.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'}
    r = session.get(str_url, headers=headers)
    dataStr = r.text
    scode = dataStr.split("#")[0]
    sxh = dataStr.split("#")[1]
    code = username + "%%%" + password
    encode = ""
    i = 0
    while i < len(code):
        if i < 20:
            encode += code[i:i + 1] + scode[0:int(sxh[i:i + 1])]
            scode = scode[int(sxh[i:i + 1]):len(scode)]
        else:
            encode += code[i:len(code)]
            i = len(code)
        i += 1
    return encode


# 获取验证码
def get_verify_code(session):
    img_url = 'https://jw.educationgroup.cn/gzasc/verifycode.servlet'
    headers = {
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'jw.educationgroup.cn',
        'Referer': 'https://jw.educationgroup.cn/gzasc/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'
    }
    r = session.get(img_url, headers=headers)

    # 机器识别验证码
    # 保存图片
    path = './code/'  # 图片路径
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + 'verify_code.png', 'wb') as f:
        f.write(r.content)

    # 识别验证码
    # code = recognize(path + 'verify_code.png')
    ocr = ddddocr.DdddOcr()
    with open(path + 'verify_code.png', 'rb') as f:
        image = f.read()
    code = ocr.classification(image)
    # print('识别结果:', code)
    return code


# 登录
def login(encoded, verify_code, session):
    login_url = 'https://jw.educationgroup.cn/gzasc/Logon.do?method=logon'
    data = {
        'userAccount': '',
        'userPassword': '',
        'encoded': encoded,
        'RANDOMCODE': verify_code
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '101',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'jw.educationgroup.cn',
        'Origin': 'https://jw.educationgroup.cn',
        'Referer': 'https://jw.educationgroup.cn/gzasc/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'}
    r = session.post(login_url, headers=headers, data=data)
    try:
        html = etree.HTML(r.text)
        error = html.xpath('//font[@color="red"]/text()')[0]
        return '4002'
    except:
        return '2002'
