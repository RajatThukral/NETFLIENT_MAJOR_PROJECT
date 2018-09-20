from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from textblob import TextBlob
from afinn import Afinn
import re
from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
from nltk.stem import WordNetLemmatizer
import uuid
import codecs
import twitter_sentiment_module as tsa
lm = WordNetLemmatizer()
af = Afinn()

#consumer key, consumer secret, access token, access secret.
consumer_key = '3LNniN3hkF1ONk95RrYZhDKHQ'
consumer_secret = 'C1O6NQwkaQEejsSQJyMTywJhdh6EdWDdEyqZY1kKJ0zYOh2zco'
access_token = '874951707058348032-q6B3QyzWL9m3MeOoYE7Ks34Jb1cxJkG'
access_secret = 'MynU2mhSvgBnaPHITmmG0T7FTgWg0Wz1sHSTZCvm9fCG6'

tok = WordPunctTokenizer()
pat1 = r'@[A-Za-z0-9_]+'
pat2 = r'https?://[^ ]+'
combined_pat = r'|'.join((pat1, pat2))
www_pat = r'www.[^ ]+'
negations_dic = {"isn't":"is not", "aren't":"are not", "wasn't":"was not", "weren't":"were not",
                "haven't":"have not","hasn't":"has not","hadn't":"had not","won't":"will not",
                "wouldn't":"would not", "don't":"do not", "doesn't":"does not","didn't":"did not",
                "can't":"can not","couldn't":"could not","shouldn't":"should not","mightn't":"might not",
                "mustn't":"must not"}

neg_pattern = re.compile(r'\b(' + '|'.join(negations_dic.keys()) + r')\b')

def tweet_cleaner_updated(text):
    blob = TextBlob(text)

    try:
        text = str(blob.translate(to = 'en'))
        text = text.replace("# ","#")
        text = text.replace("@ ","@")
        text = text.replace(" _ ","_")
    except:
        text = text

    text = re.compile('#\w+ ').sub('', re.compile('RT @\w+: ').sub('', text, count=1)).strip()
    text = re.compile('RT @').sub('@', text, count=1)
    soup = BeautifulSoup(text, 'lxml')
    souped = soup.get_text()

    try:
        bom_removed = souped.decode("utf-8-sig").replace(u"\ufffd", "?")
    except:
        bom_removed = souped
    stripped = re.sub(combined_pat, '', bom_removed)
    stripped = re.sub(www_pat, '', stripped)
    lower_case = stripped.lower()
    neg_handled = neg_pattern.sub(lambda x: negations_dic[x.group()], lower_case)
    letters_only = re.sub("[^a-zA-Z]", " ", neg_handled)
    words = [x for x  in tok.tokenize(letters_only) if len(x) > 1]
    lemma = [lm.lemmatize(w) for w in words]
    return (" ".join(lemma)).strip()

def tweet_cleaner(text):
    blob = TextBlob(text)
    try:
        text = str(blob.translate(to = 'en'))
        text = text.replace("# ","#")
        text = text.replace("@ ","@")
        text = text.replace(" _ ","_")
    except:
        text = text

    text = re.compile('#\w+ ').sub('', re.compile('RT @\w+: ').sub('', text, count=1)).strip()
    text = re.compile('RT @').sub('@', text, count=1)
    soup = BeautifulSoup(text, 'lxml')
    souped = soup.get_text()

    try:
        bom_removed = souped.decode("utf-8-sig").replace(u"\ufffd", "?")
    except:
        bom_removed = souped
    stripped = re.sub(combined_pat, '', bom_removed)
    stripped = re.sub(www_pat, '', stripped)
    lower_case = stripped.lower()
    neg_handled = neg_pattern.sub(lambda x: negations_dic[x.group()], lower_case)
    letters_only = re.sub("[^a-zA-Z]", " ", neg_handled)
    words = [x for x  in tok.tokenize(letters_only) if len(x) > 1]
    return (" ".join(words)).strip()

class StdOutListener(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data)
        tweet = all_data["text"]
        username = all_data['user']['screen_name']
        userprofile = all_data['user']['profile_image_url']
        followers_count = all_data['user']['followers_count']
        print(tweet.replace("\xe2\x80\x99","'").encode("utf-8"))
        cleaned_tweet = tweet_cleaner_updated(tweet)
        sentiment_prediction = tsa.sentiment(cleaned_tweet)
        sentiment_prediction_str = ','.join(str(x) for x in sentiment_prediction)
        tweet_others = tweet_cleaner(tweet)
        af_score = af.score(tweet_others)

        words = [w for w in tweet_others.split()]
        score_list = [af.score(w) for w in tweet_others.split()]

        total = len(tweet_others.split())

        def file_name():
            with open('trash.txt', 'r') as fpr:
                for lines in fpr.readlines():
                    return lines
        try:
            comp = round(af_score/total,2)
            comp = abs(comp)

        except:
            comp = '--'
        pos_words = []
        neg_words = []

        for a,b in zip(words,score_list):
            if(b>0):
                pos_words.append(a)
            elif(b<0):
                neg_words.append(a)

        pos_w = ", ".join(pos_words)
        neg_w = ", ".join(neg_words)

        if(pos_w == ''):
            pos_w = '--'

        if(neg_w == ''):
            neg_w = '--'
        blob2 = TextBlob(tweet_others)

        tb_blob_sentiment = blob2.sentiment.polarity
        tb_blob_subjectivity = blob2.sentiment.subjectivity

        tb_blob_sentiment = round(tb_blob_sentiment,2)
        tb_blob_subjectivity = round(tb_blob_subjectivity,2)

        t = file_name()
        save_sentiment = open("static/tsa/"+t+".txt",'a')
        save_sentiment.write(sentiment_prediction_str)
        save_sentiment.write('||')
        save_sentiment.close()

        save_tweets = open("static/tsa/"+t+".txt",'ab')
        save_tweets.write(tweet.encode("utf-8"))
        save_tweets.write('||'.encode())
        save_tweets.close()

        s1 = open("static/tsa/"+t+".txt",'a')
        s1.write(str(followers_count))
        s1.write('||')
        s1.close()

        s111 = open("static/tsa/"+t+"_sentiment.txt",'a')
        s111.write(sentiment_prediction_str)
        s111.write('\n')
        s111.close()

        s2 = open("static/tsa/"+t+".txt",'a')
        s2.write(username)
        s2.write('||')
        s2.close()

        s3 = open("static/tsa/"+t+".txt",'a')
        s3.write(userprofile)
        s3.write('||')
        s3.close()

        s4 = open("static/tsa/"+t+".txt",'a')
        s4.write(str(af_score))
        s4.write('||')
        s4.close()

        s5 = open("static/tsa/"+t+".txt",'a')
        s5.write(str(tb_blob_sentiment))
        s5.write('||')
        s5.close()

        s6 = open("static/tsa/"+t+".txt",'a')
        s6.write(str(tb_blob_subjectivity))
        s6.write('||')
        s6.close()

        s7 = open("static/tsa/"+t+".txt",'a')
        s7.write(pos_w)
        s7.write('||')
        s7.close()

        s8 = open("static/tsa/"+t+".txt",'a')
        s8.write(neg_w)
        s8.write('||')
        s8.close()

        s9 = open("static/tsa/"+t+".txt",'a')
        s9.write(str(comp))
        s9.write('|||||')
        s9.close()

        save_clean_tweets = open("_cleaned.txt",'ab')
        save_clean_tweets.write(cleaned_tweet.encode("utf-8"))
        save_clean_tweets.write('|||'.encode())
        save_clean_tweets.close()

        print(userprofile)
        print(username)
        print(af_score)
        print(followers_count)
        print(sentiment_prediction)

        return True

    def on_error(self, status):
        print (status)


auth = OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_secret)
twitterStream = Stream(auth, StdOutListener())

def streaminging(twitter_tag):
    twitterStream.filter(track=[twitter_tag], async=False)
