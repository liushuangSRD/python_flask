# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from flask import Flask, json, jsonify, render_template, request
import requests
import calendar
import datetime
import pandas as pd

app = Flask(__name__, static_url_path='')


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def get_empcode(username, password):
    # 登录获取header
    data = 'userid=' + username + '&linkpage=&userName=' + username + '&j_username=' + username + '&password=' + password + '&j_password=' + password
    url = 'http://ics.chinasoftinc.com/login?' + data
    req = requests.post(url)
    header = req.request.headers
    print(header)

    # 获取empCode
    url = 'http://ics.chinasoftinc.com:8010/sso/toLoginYellow'
    req = requests.get(url=url, headers=header)
    res = req.url
    emp_code = res.split('empCode=')
    if len(emp_code) > 1:
        emp_code = emp_code[1]
    print(emp_code)

    # 获取userToken
    url = 'http://ics.chinasoftinc.com:8010/ehr_saas/web/user/loginByEmpCode.jhtml'
    data = {'empCode': emp_code}
    print(data)
    headerss = {'Content-Type': 'application/json;charset=UTF-8'}
    print(headerss)
    req = requests.post(url=url, headers=headerss, data=json.dumps(data))
    result = req.json()
    print(result)
    if result['errorCode'] == '0':
        return result['result']['data']['token']
    else:
        return None


@app.route('/')
def login():
    return render_template('add.html')


@app.route('/getTime', methods=['POST'])
def get_data():
    json_data = request.get_json()
    print(request.form)
    if 'username' not in json_data or 'password' not in json_data:
        return
    username = json_data['username']
    password = json_data['password']
    token = get_empcode(username, password)
    if token is None:
        token = get_empcode(username, password)
    if token is None:
        return jsonify({'errno': '1', 'errmsg': '账号密码错误'})
    url = 'http://ics.chinasoftinc.com:8010/ehr_saas/web/attEmpLog/getAttEmpLogByEmpId2.empweb'
    today = datetime.date.today()
    ranges = calendar.monthrange(today.year, today.month)
    days = pd.bdate_range(str(today.month) + '/' + str(ranges[0] + 1) + '/' + str(today.year),
                          str(today.month) + '/' + str(ranges[1])
                          + '/' + str(today.year))
    print(days[0])
    return_list = []
    for dt in days:
        result = get_result(dt, token, url)
        if result is None:
            result = get_result(dt, token, url)
        if 'out' in result and result['out'] is not None and result['out'] != '':
            outTime = datetime.datetime.strptime(result['out'], '%H:%M:%S')
            outBZ = datetime.datetime.strptime(result['outBZ'], '%H:%M:%S')
            if (outTime - outBZ).total_seconds() < 0:
                result['red'] = True

        result['addSec'] = get_add(result)
        if result['addSec'] is not None:
            result['addMinute'] = round((result['addSec'] / 60.0), 2)
        return_list.append(result)
        totalAdd = 0
        count = 0
        for res in return_list:
            if res['addSec'] is not None:
                totalAdd += res['addSec']
                count = count + 1
        totalAdd = round((totalAdd / 3600), 2)
        percent = round((totalAdd / count), 2)
    return jsonify({'errno': '0', 'data': return_list, 'totalAdd': totalAdd, 'percent': percent})


def get_add(result):
    if result is None:
        return None
    if 'in' in result and result['in'] is not None and result['in'] != '':
        inTime = datetime.datetime.strptime(result['in'], '%H:%M:%S')
        outTime = datetime.datetime.strptime(result['out'], '%H:%M:%S')
        inBZ = datetime.datetime.strptime(result['inBZ'], '%H:%M:%S')
        outBZ = datetime.datetime.strptime(result['outBZ'], '%H:%M:%S')

        minusStart = datetime.datetime.strptime('18:00:00', '%H:%M:%S')
        minusEnd = datetime.datetime.strptime('18:30:00', '%H:%M:%S')
        # 5点半班次
        minusBEnd = datetime.datetime.strptime('17:30:00', '%H:%M:%S')
        inDe = (inBZ - inTime).total_seconds()

        if (outBZ - minusBEnd).total_seconds() == 0:
            minusStart = outBZ
            minusEnd = minusStart

        if (outTime - minusEnd).total_seconds() >= 0:
            addTime = inDe + (outTime - outBZ).total_seconds() - 1800
        elif (outTime - minusStart).total_seconds() >= 0:
            addTime = inDe + (minusStart - outBZ).total_seconds()
        else:
            if (outTime - outBZ).total_seconds() > 0:
                addTime = inDe + (outTime - outBZ).total_seconds()
            else:
                addTime = inDe

        return addTime
    else:
        return None


def get_result(dt, token, url):
    header = {'Content-Type': 'application/json;charset=UTF-8', 'token': token}
    dateStr = dt.strftime("%Y-%m-%d %H:%M:%S")
    date_result = dt.strftime("%Y-%m-%d")
    data = {'dt': dateStr}
    req = requests.post(url=url, data=json.dumps(data), headers=header)
    result = req.json()
    if result['errorCode'] == '0':
        attEmpDetail = result['result']['data']['attEmpDetail']
        if 'checkIn' in attEmpDetail:
            dtDetailList = attEmpDetail['dtDetailList']
            re = {'dt': date_result, 'inBZ': dtDetailList[0]['checkInBZ'], 'outBZ': dtDetailList[0]['checkOutBZ'],
                  'in': attEmpDetail['checkIn'], 'out': attEmpDetail['checkOut']}
            return re
        else:
            return {}
    else:
        return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
