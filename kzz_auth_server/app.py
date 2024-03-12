import time

from gdyk.verify import verify
from flask import Flask, jsonify, request
from gdyk.login import main_login
from gdyk.score import getScore

app = Flask(__name__)


@app.route('/gdyk/hello')
def hello_world():  # put application's code here
    response = {}
    response['code'] = '2000'
    response['message'] = '获取成功'
    response['data'] = "Demo Flask & Docker application is up and running!"
    return response


@app.route('/gdyk/login', methods=["POST"])
def login():
    response = {}
    data = request.get_json()
    userAccount = data["userAccount"]
    userPassword = data["userPassword"]
    xnxq01id = data["xnxq01id"]
    max_attempts = 2
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        schedule_data, school_calendar, school_weeks, statusCode = main_login(userAccount, userPassword, xnxq01id)

        if statusCode == '2002':  # login success
            if schedule_data == [] or school_calendar == []:
                response['code'] = '5001'
                response['message'] = '获取失败'
            else:
                response['data'] = {'schedule_data': schedule_data, 'school_calendar': school_calendar,
                                    'school_weeks': school_weeks}
                response['code'] = '2001'
                response['message'] = '获取成功'
            break  # 成功则跳出循环
        elif statusCode == '4002':  # login fail
            if attempts >= max_attempts:
                response['code'] = '4002'
                response['message'] = '登录失败,账号或密码出错'
            else:
                print(f"登录失败，正在进行第 {attempts} 次重试...")
                time.sleep(1)  # 等待1秒后重试

    return jsonify(response)


@app.route('/gdyk/score', methods=["POST"])
def score():
    response = {}
    data = request.get_json()
    userAccount = data["userAccount"]
    userPassword = data["userPassword"]
    xnxq01id = data["xnxq01id"]

    max_retries = 2
    retry_wait = 1

    for retry in range(max_retries + 1):
        score, statusCode = getScore(userAccount, userPassword, xnxq01id)
        if len(score) > 0:
            response['data'] = score
            response['code'] = '2003'
            response['message'] = '获取成绩成功'
            break  # 成功获取成绩，退出重试循环
        else:
            if retry < max_retries:
                print(f"获取成绩失败，正在进行第 {retry + 1} 次重试...")
                time.sleep(retry_wait)  # 等待一段时间再进行重试
            else:
                response['code'] = '5002'
                response['message'] = '获取成绩失败'
    return jsonify(response)


@app.route('/gdyk/verify', methods=["POST"])
def verify_identity():
    response = {}
    data = request.get_json()
    userAccount = data["userAccount"]
    userPassword = data["userPassword"]
    max_attempts = 2
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        statusCode = verify(userAccount, userPassword)

        if statusCode == '2002':  # login success
            response['code'] = '2006'
            response['message'] = '验证成功'
            break  # 成功则跳出循环
        elif statusCode == '4002':  # login fail
            if attempts >= max_attempts:
                response['code'] = '5006'
                response['message'] = '账号或密码出错'
            else:
                print(f"验证失败，正在进行第 {attempts} 次重试...")
                time.sleep(1)  # 等待1秒后重试

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
