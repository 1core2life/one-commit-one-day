
from flask import Flask, jsonify, request, render_template, redirect, url_for
import os
# from module.question import Question
import requests
from bs4 import BeautifulSoup

import random
import json
import datetime
from pytz import timezone

app = Flask(__name__,  static_url_path='/static')

LAST_COUNT = 0

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/total", methods=['POST'])
def get_total_fine():
    return jsonify({'total_fine':total_fine*1000})


@app.route("/users", methods=['POST'])
def get_user_list():
    last_saturday =  get_last_saturday(LAST_COUNT)
    last_last_saturday =  get_last_saturday(LAST_COUNT + 1)

    users = read_user_list()
    global total_fine
    total_fine = 0
    for user in users:
        url = "https://github.com/" + user["id"]
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        user["profile"] = soup.find(class_="avatar-user")["src"]

        start_date = datetime.datetime.strptime(user['start_date'].strip(), '%Y-%m-%d')
        commit = int(0)
        consecutive = int(0)
        new_fine = int(0)
        fine = int(0)
        total_day = int(0)

        for rect in soup.find_all('rect'):
            if not rect.get('data-date'):
                continue
        
            data_date = datetime.datetime.strptime(rect.get('data-date'), '%Y-%m-%d')
            if last_saturday < data_date:
                continue

            if start_date < data_date: 
                total_day = total_day + 1
                   
                date_commit = int(rect.get('data-level'))
                if date_commit > 0:
                    consecutive = consecutive + 1
                else:
                    if last_last_saturday < data_date and last_saturday >= data_date:
                        new_fine = new_fine + 1
                    consecutive = 0
                    fine = fine + 1

                commit = commit + date_commit
                
        total_fine = total_fine + fine
 
        user["commit"] = commit
        user["consecutive_date"] = consecutive
        user["fine"] = fine
        user["new_fine"] = new_fine

        state = commit / total_day * 100
        if state <= 60:
            user["state"] = "danger"
            user["state_text"] = "F"
        elif state <= 70:
            user["state"] = "warning"
            user["state_text"] = "D"
        elif state <= 80:
            user["state"] = "warning"
            user["state_text"] = "C"
        elif state <= 90:
            user["state"] = "warning"
            user["state_text"] = "B"
        else:
            user["state"] = "success"
            user["state_text"] = "A"
    
    users.sort(key=lambda user: user["commit"], reverse=True)
            


    return render_template("user.html", result=users)


# count = 0 > last, 1 > last-last, 2 > last-last-last
def get_last_saturday(count):
    today = datetime.datetime.strptime(datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d'), ('%Y-%m-%d'))
    idx = (today.weekday() + 1) % 7
    sat = today - datetime.timedelta(7 + idx - 6 + count*7)

    return sat
    




def read_user_list():
    users = list()

    f = open("./user_list.txt", 'r')
    lines = f.readlines()
    for line in lines:
        splitted = line.split(' ')
        user = dict()
        user["id"] = splitted[0]
        user["name"] = splitted[1]
        user["start_date"] = splitted[2]

        users.append(user)

    f.close()

    return users

def get_test_data(users):

    user = dict()
    user["name"] = "백지원"
    user["start_date"] = "06/05/2021"
    user["commit"] = "25"
    user["consecutive_date"] = "8"
    user["fine"] = "1,000"
    user["new_fine"] = "1,000"
    # Success / warning / Danger
    user["state"] = "warning"
    
    users.append(user)


    user = dict()
    user["name"] = "백지원"
    user["start_date"] = "06/05/2021"
    user["commit"] = "25"
    user["consecutive_date"] = "8"
    user["fine"] = "1,000"
    # Success / warning / Danger
    user["state"] = "warning"
    
    users.append(user)

    return users


if __name__ == '__main__':
    app.debug = True
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 80)))

