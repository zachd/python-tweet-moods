import tweepy
import json
import socket
import time
from textblob import TextBlob
from textblob import Blobber
from textblob.sentiments import NaiveBayesAnalyzer
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from threading import Lock

API_KEY = ''
consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

# initial tweepy code from source below
# http://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/ 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# udp packet: http://stackoverflow.com/q/18743962
IP = ''
PORT = 0

# mutex global mood variables
mutex = Lock()
sad = 0
happy = 0
neutral = 0

# train analyzer before run: http://stackoverflow.com/a/33360383
tb = Blobber(analyzer=NaiveBayesAnalyzer())

# defualt listener class for tweepy streaming
class MyListener(StreamListener):
    def on_data(self, data):
        # use global variables outside class
        global tb, sad, happy, neutral
        # convert to json and get text
        jsondata = json.loads(data)
        tweet = jsondata.get("text")
        print("[INFO] Received \"" + tweet + "\"")
        # text blob naive bayesian: https://textblob.readthedocs.org/en/dev/advanced_usage.html#sentiment-analyzers
        blob = tb(tweet)
        # acquire moods mutex
        mutex.acquire()
        try:             
            # set positive, negative and neutral moods
            if(blob.sentiment.p_pos > 0.5):
                happy += 1
            elif(blob.sentiment.p_neg > 0.5):
                sad += 1
            else:
                neutral += 1
            print("[INFO] happy:" + str(happy) + " | n:" + str(neutral) + " | sad:" + str(sad) + " [+" + str(blob.sentiment.p_pos) + " -" + str(blob.sentiment.p_neg) + "]")
        finally:
            # release moodsmutex
            mutex.release()
        return True
 
    def on_error(self, status):
        print("[WARNING] error returned from twitter")
        return True

# initialize stream with tracking tag and set toa sync
twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(track=['python'], async=True)

# loop every 3 minutes and send data 
while(True):
    time.sleep(180)
    # get mutex so async thread doesnt interfere
    mutex.acquire()
    try:
        try:      
            # send all three mood statistics to hosted graphite
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock.sendto(API_KEY + ".happy " + str(happy), (IP, PORT))
            sock.sendto(API_KEY + ".sad " + str(sad), (IP, PORT))
            sock.sendto(API_KEY + ".neutral " + str(neutral), (IP, PORT))
            sock.close()
            print("[INFO] sending data [h:" + str(happy) + " n:" + str(neutral) + " s:" + str(sad) + "]")
            # reset mood variables
            happy = 0   
            sad = 0
            neutral = 0
        except Exception as e:
            print("[WARNING] error sending data")
    finally:
        mutex.release()
