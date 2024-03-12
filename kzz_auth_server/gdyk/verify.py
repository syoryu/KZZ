# —*— coding: utf-8 —*—
# @Time:    2023/2/14 22:09
# @Author:  syoryu
# @File:    强智教务系统验证身份.py
# @Software:PyCharm
import logging

import ddddocr
import requests
import os
from lxml import etree
from gdyk.recognize import recognize


def verify(username, password):
    username = username
    password = password
    session = get_cookie()  #
    verify_code = get_verify_code(session)  #
    encoded = get_code(username, password, session)  #
    statusCode = login(encoded, verify_code, session)  #
    return statusCode


#
def get_cookie():
    host = 'https://jw.educationgroup.cn/gzasc/'
    session = requests.session()
    session.get(host, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'
    })
    return session


#
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

    logging.info("code" + code)
    logging.info("sxh" + sxh)

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

    #
    #
    path = './code/'  #
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


#
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
        # print('err', r.text)
        return '4002'
    except:
        # print('success', r)
        return '2002'
