from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sentiment_module as sa


#consumer key, consumer secret, access token, access secret.
consumer_key = '3LNniN3hkF1ONk95RrYZhDKHQ'
consumer_secret = 'C1O6NQwkaQEejsSQJyMTywJhdh6EdWDdEyqZY1kKJ0zYOh2zco'
access_token = '874951707058348032-q6B3QyzWL9m3MeOoYE7Ks34Jb1cxJkG'
access_secret = 'MynU2mhSvgBnaPHITmmG0T7FTgWg0Wz1sHSTZCvm9fCG6'

class listener(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data)
        tweet = all_data["text"]
        sentiment_value, confidence = sa.sentiment(tweet)
        print((tweet).encode("utf-8"), sentiment_value, confidence)
        if confidence*100 >= 0:
            output = open("twitter-out.txt","a")
            output.write(sentiment_value)
            output.write('\n')
            output.close()
        return True

    def on_error(self, status):
        print (status)

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["#ToiletEkPremKatha"])
