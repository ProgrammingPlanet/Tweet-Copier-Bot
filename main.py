import tweepy, time
from random import random as rand
from sys import argv
from threading import Thread

import database
from auth import sign_up, sign_in

db = database.read()

API_KEY = db['config']['api_key']
API_SECRET_KEY = db['config']['api_secret']
sleep_time = db['config']['sleep_time_sec']

app = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)

tweets_queue = []

def signup():
	global app, db
	api,users = sign_up(app, tweepy.API, db['users'])
	if users != None:
		db.update({'users': users})
		database.write(db)
		print('sign up successfull.')
	else:
		print('sign up error.')

def post_tweet():
	global tweets_queue
	try:
		api, tweet_text = tweets_queue.pop(0) #first one
		api.update_status(status=tweet_text)
	except Exception as e:
		print(e)

def fetch_tweets():
	global app, db, tweets_queue
	for id,user in db['users'].items():
		api = tweepy.API(sign_in(app, db['users'], id))
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
							tweets_queue.append((api, tweet.full_text))
			db['users'][id]['copies'][target_id]['last_copy_tweeted_at'] = most_recent_tweet_time_gmt
	database.write(db)


if '--signup' in argv:
	signup()
	exit(0)

fetch_tweets_thread = Thread(target=fetch_tweets)
post_tweet_thread = Thread(target=post_tweet)

while True:
	try:
		if not fetch_tweets_thread.is_alive():
			fetch_tweets_thread.start()
		if not post_tweet_thread.is_alive():
			post_tweet_thread.start()
	except Exception as e:
		print(e)









