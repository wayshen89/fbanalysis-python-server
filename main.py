import pandas as pd
import string
import sys
import requests
import facebook
import json
import nltk
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request,session, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField,StringField,SubmitField
from PIL import Image
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

matplotlib.use('Agg')

def getFacebookPageMessageFromFacebookAPI(token, pageid):
    graph = facebook.GraphAPI(access_token= token, version ="3.1")
    posts = graph.get_object(id=pageid+'/conversations', fields='messages{message}')

    allMessages = []
    while(True):
        try:
                #get conversations
            conversations = posts["data"]
                    
                #loop conversations
            for conversation in conversations:
                convo = conversation["messages"]
                        
                while(True):
                    try:
                            #get messages
                        messages = convo["data"]
                            #Loop messages
                        for message in messages:
                            allMessages.append(message["message"])
                                
                            #get message next page
                        nextmessages = convo["paging"]["next"]
                        convo = requests.get(nextmessages).json()
                            
                    except KeyError:
                         break
                #get conversation next page
            conversation_next = posts["paging"]["next"]
            posts = requests.get(conversation_next).json()
        except KeyError:
            break
    return allMessages

def generateWordCloud(pageid,data):
    wc = WordCloud(max_font_size=75, max_words=100,width=500, height=400,collocations=False,
                background_color='white',scale=1,relative_scaling=0.5).generate(str(data))
    filename = pageid+'_wordcloud.png'
    plt.imshow(wc,interpolation='bilinear')
    plt.axis("off")
    plt.savefig('static/'+filename)
    plt.clf()
    return os.path.join('static', filename)

def performSentimentAnalysis(pageid,data):
    analyse = SentimentIntensityAnalyzer()
    summary = {"positive":0,"neutral":0,"negative":0}
    for x in data: 
        ss = analyse.polarity_scores(x)
        if ss["compound"] == 0.0: 
            summary["neutral"] +=1
        elif ss["compound"] > 0.0:
            summary["positive"] +=1
        else:
            summary["negative"] +=1

    lists = sorted(summary.items())
    x, y = zip(*lists)
    filename = pageid+'_chart.png'
    plt.bar(x, y)
    plt.savefig('static/'+filename)
    plt.clf()
    return os.path.join('static', filename)

app = Flask(__name__,template_folder='template')

@app.route("/", methods=['GET', 'POST'])
def run():
    if request.method == 'GET':
        return render_template('form.html')
    if request.method == 'POST':
        token = request.form.get('token')
        pageid = request.form.get('pageid')
        data = getFacebookPageMessageFromFacebookAPI(token, pageid)
        wordclodFilename = generateWordCloud(pageid,data)
        sentimentAnalysisFilename = performSentimentAnalysis(pageid,data)
        return render_template("result.html", wordclodFilename = wordclodFilename, sentimentAnalysisFilename=sentimentAnalysisFilename)


if __name__ == "__main__":
    app.run()
 
