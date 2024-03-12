# coding=utf8
import requests
import ddddocr
import os
from lxml import etree
from gdyk.recognize import recognize
from gdyk.schedule import schedule
from gdyk.schoolCalendar import schoolCalender


# 主登录函数
def main_login(username, password, xnxq01id):
    username = username  # 学号
    password = password  # 密码
    xnxq01id = xnxq01id # 查询学期 2022-2023-2

    session = get_cookie()  # 获取登录会话
    print("session", session)
    verify_code = get_verify_code(session)  # 验证码验证
    print("verify_code", verify_code)
    encoded = get_code(username, password, session)  # 获取加密算法
    statusCode = login(encoded, verify_code, session)  # 获取登录状态码

    if statusCode == '2002':  # 登录成功状态码
        schedule_data = get_schedule(xnxq01id, session)  #
        school_calender, school_weeks = get_schoolCalender(xnxq01id, session)  #
        return schedule_data, school_calender, school_weeks, statusCode
    elif statusCode == '4002':  # 登录失败状态码
        return [], [], [], statusCode


# 获取cookie
def get_cookie():
    host = 'https://jw.educationgroup.cn/gzasc/'
    session = requests.session()
    session.get(host, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'
    })
    return session


# 获取加密算法
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


#
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

    # 将获取的验证码图片存储到本地
    path = './code/'  #
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + 'verify_code.png', 'wb') as f:
        f.write(r.content)
    # 识别验证码
    ocr = ddddocr.DdddOcr()
    with open(path + 'verify_code.png', 'rb') as f:
        image = f.read()
    code = ocr.classification(image)
    return code


# 登录函数
def login(encoded, verify_code, session):
    login_url = 'https://jw.educationgroup.cn/gzasc/Logon.do?method=logon'
    # 请求负载
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
        return '4002'  # 登录失败
    except:
        # print('success', r)
        return '2002'  # 登录成功


# 获取课程表
def get_schedule(xnxq01id, session):
    host = 'https://jw.educationgroup.cn/gzasc_jsxsd/xskb/xskb_list.do'
    data = {
        'zc': '',  # 不知道是什么东西
        'xnxq01id': xnxq01id,  # 查询学期
        'sfFD': '1',  # 页面放大
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
        'Referer': 'https://jw.educationgroup.cn/gzasc_jsxsd/framework/xsMain.jsp',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'}
    response = session.post(host, headers=headers, data=data)
    text = response.text
    return schedule(response.text)  # 获取课程表页面html


# 获取校历
def get_schoolCalender(xnxq01id, session):
    host = 'https://jw.educationgroup.cn/gzasc_jsxsd/jxzl/jxzl_query'
    data = {
        'xnxq01id': xnxq01id,  # 查询学期
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '101',
        'Host': 'jw.educationgroup.cn',
        'Referer': 'https://jw.educationgroup.cn/gzasc_jsxsd/framework/xsMain.jsp',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'}
    response = session.post(host, headers=headers, data=data)
    return schoolCalender(response.text)
