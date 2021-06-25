
from flask import Flask, jsonify, request, render_template

import pandas as pd
import numpy as np 
import math
import re
#import json
import requests
from datetime import datetime,date
# from datetime import datetime  
from datetime import timedelta 
import time
#from requests.auth import HTTPBasicAuth
from flask import json

from recommender import DeveloperRecommender


from collections import Counter

app= Flask(__name__)

@app.route("/")
def index():
    return render_template("inputForm.html")
    # return

#@app.route("/login")
#return render_template("loginForm.html")

def getUserActivityMean(username):
    url = f'https://api.github.com/users/{username}/events?access_token=e4bb0633cb28ddbf5a07518ae14f6d80627191a3'
    s =  requests.Session()
    req = s.get(url)
    res =  req.json()
    activeTime = []
    push_count = 0
    
    # print(res)
    # return
    for x in res:
        # print(x)
        activeTime.append(x['created_at'])
        if x['type'] == "PushEvent":
            push_count +=1

    items = [pd.to_datetime(y) for y in activeTime]
    
    seriesData = pd.Series(items)
    averageTime = seriesData.mean()

    averageDateTime = averageTime.to_pydatetime()

    return averageDateTime.strftime("%H:%M:%S"),push_count

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def get_range_time(activity_time, delta_type):
    delta = timedelta(hours = 2)
   
    current_date = datetime.today()
   
    
    time_obj = datetime.combine(date(current_date.year,current_date.month,current_date.day),activity_time)
 
    if delta_type == "add":
        return (time_obj + delta).time()
    else:
        return (time_obj - delta).time()

def check_in_time_range(activityTime , time_required):
    time_obj = datetime.strptime(time_required,"%H:%M:%S").time()
    activityTime_obj = datetime.strptime(activityTime,"%H:%M:%S").time()
  
    upper_time = get_range_time(time_obj,"add")
    lower_time =  get_range_time(time_obj,"sub")
 
    return time_in_range(lower_time,upper_time,activityTime_obj)


@app.route("/developer", methods=['POST', 'GET'])
def developerList():

    if request.method == 'POST':

        request_body = request.get_json()
        issue_title =  request_body['issue']
        time_required = request_body['time']
        
        pr_data = pd.read_csv("github-repo-commit-dataset.csv")
        isssue_data = pd.read_csv("issues-dataset.csv")

        developer_recommender = DeveloperRecommender(pr_data,isssue_data)

        developers = developer_recommender.recommender_developer(issue_title)
        recommended_developer_list = []


        for userItem in developers:

            activityTime,push_count = getUserActivityMean(userItem.get("user"))

            """
                Check the activity time and required time and 
                have bvariable that holds the boolean of it 
                add the boolean in the below dictionanty
            """
        
            is_available = 1 if check_in_time_range(activityTime , time_required) == True else 0

            match_score = (is_available + push_count / 100 + userItem.get("similarity")) / 3
            userInfo = {"username":userItem.get("user") , "online_time" : activityTime, "push_count":push_count , "is_available":is_available, "similarity":userItem.get("similarity"), "match_score":match_score*100}
            recommended_developer_list.append(userInfo)


        output = recommended_developer_list

        # return render_template("test.html",out=output)
        return jsonify(output)



if __name__=='__main__':
    app.run(debug=True)
    
