import tweepy
import time
from random import random as rand
from sys import argv

from config import API_KEY, API_SECRET_KEY, sleep_time

import database
from auth import sign_up, sign_in

db = database.read()

app = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)

def signup():
	global app, db
	api,users = sign_up(app, tweepy.API, db['users'])
	if users != None:
		db.update({'users': users})
		database.write(db)
		print('sign up successfull.')
	else:
		print('sign up error.')

def post_tweet(api, text):
	try:
		api.update_status(status=text)
	except Exception as e:
		print(e)

def loop():
	global app, db
	for id,user in db['users'].items():
		app = sign_in(app, db['users'], id)
		api = tweepy.API(app)
		for target_id,target in user['copies'].items():
			recent_20_tweets = api.user_timeline(user_id=target_id, tweet_mode='extended')
			most_recent_tweet_time_gmt = target['last_copy_tweeted_at']
			for tweet in recent_20_tweets:
				# print(f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}')
				if (not tweet.retweeted) and len(tweet.entities['user_mentions']) == 0 and ('media' not in tweet.entities) and (not tweet.is_quote_status) and (tweet.in_reply_to_user_id==None):
					tweet_time_gmt = round(tweet.created_at.timestamp())
					if tweet_time_gmt > target['last_copy_tweeted_at']:
						if tweet_time_gmt > most_recent_tweet_time_gmt:
							most_recent_tweet_time_gmt = tweet_time_gmt
						if rand() < target['copy_probability']: #selection based on given probablity
							post_tweet(api, tweet.full_text)
			db['users'][id]['copies'][target_id]['last_copy_tweeted_at'] = most_recent_tweet_time_gmt
	database.write(db)

if '--signup' in argv:
	signup()
	exit(0)


while True:
	try:
		loop()
		time.sleep(sleep_time)
	except Exception as e:
		print(e)









