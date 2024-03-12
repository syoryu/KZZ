# —*— coding: utf-8 —*—
# @Time:    2023/2/14 22:09
# @Author:  syoryu
# @File:    强智教务系统获取成绩.py
# @Software:PyCharm
from PIL import Image as image
from gdyk.chars import chars


# 灰值化
def covergrey(img):
    return img.convert('L')


# 清除遮挡线
def clearline(img):
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if int(img.getpixel((x, y))) >= 110:
                img.putpixel((x, y), 0xff)
            else:
                img.putpixel((x, y), 0x0)
    return img


# 识别
def identify(data):
    code = [''] * 4
    diff_min = [432] * 4
    for char in chars:
        diff = [0] * 4
        for i in range(4):
            for j in range(432):  #
                if data[i][j] != chars[char][j]:
                    diff[i] += 1
        for i in range(4):
            if diff[i] < diff_min[i]:
                diff_min[i] = diff[i]
                code[i] = char
    return ''.join(code)


# 降噪
def del_noise(im, pnum=3):
    w, h = im.size
    white = 255
    black = 0
    for i in range(0, w):
        im.putpixel((i, 0), white)
        im.putpixel((i, h - 1), white)
    for i in range(0, h):
        im.putpixel((0, i), white)
        im.putpixel((w - 1, i), white)
    for i in range(1, w - 1):
        for j in range(1, h - 1):
            val = im.getpixel((i, j))
            #
            if val == black:
                cnt = 0
                for ii in range(-1, 2):
                    for jj in range(-1, 2):
                        if im.getpixel((i + ii, j + jj)) == black:
                            cnt += 1
                if cnt < pnum:
                    im.putpixel((i, j), white)
            else:
                cnt = 0
                for ii in range(-1, 2):
                    for jj in range(-1, 2):
                        if im.getpixel((i + ii, j + jj)) == black:
                            cnt += 1
                if cnt >= 7:
                    im.putpixel((i, j), black)
    return im


# 二值化
def two_value(code_data):
    table = []
    for i in code_data:
        if i < 140:  #
            table.append(0)
        else:
            table.append(1)
    return table


# 预处理
def pre_img(path):
    img = image.open(path)
    img = covergrey(img)  # 灰值化
    img = clearline(img)  # 清除线
    img = del_noise(img)  # 降噪
    return img


# 获取目标以验证码图片
def data_img(img):
    code_data = []
    for i in range(4):
        x = 5 + i * 18
        code_data.append(img.crop((x, 9, x + 18, 33)).getdata())
        code_data[i] = two_value(code_data[i])
    return code_data

# 主函数
def recognize(path):
    img = pre_img(path)  # 预处理
    data = data_img(img)  # 二进制数据
    code = identify(data)  # 识别验证码
    return code
