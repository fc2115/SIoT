#!/usr/bin/python

from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import regex
import csv
import pandas as pd
import requests
import twitter_credentials
import gspread
from oauth2client.service_account import ServiceAccountCredentials

###############################################################################
#
# THIS SECTION IS FOR MINING THE CURRENCY DATA VALUES AND STORING LOCALLY
#
###############################################################################

# Api request for currency value. API is the last set of characters in the string
data = requests.get("https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=GBP&to_currency=EUR&apikey=XS6HGF3HNDE1MR45")

# Format the data from json into dictionary
data = data.json()

# Only require the actual exchange value, the data and time, and the Timezone.
exchange_rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
data_time = data['Realtime Currency Exchange Rate']['6. Last Refreshed']
time_zone = data['Realtime Currency Exchange Rate']['7. Time Zone']

Real_vals_dict = {'Exchange Rate': [exchange_rate], 'Date and Time': [data_time], 'Time Zone': [time_zone]}

# Put the data into a pd dataframe for easy csv writing
df = pd.DataFrame(Real_vals_dict)
print(df)

# write the data to a separate csv file
df.to_csv('GBP_EUR_rates.csv', mode = 'a', index=False,  header=None)

###############################################################################
#
# THIS SECTION IS FOR MINING THE TWEETS WITH BREXIT INCLUDED AND STORING THE
# DATA LOCALLY
#
###############################################################################

def print_tweet(tweet):
    print(tweet.user.screen_name, tweet.user.name, tweet.created_at, tweet.id)
    print(tweet.full_text)

    # Checks to ensure data is legitimate
    print("Replying to a profile ID ", tweet.in_reply_to_user_id)
    print("Replying to a profile ID string ", tweet.in_reply_to_user_id_str)
    print("Replying to a status ", tweet.in_reply_to_status_id)
    print("Replying to a status string", tweet.in_reply_to_status_id_str    )
    print("Retweet Status ", tweet.retweeted)


def process_results(results):
    id_list = [tweet.id for tweet in results]
    data_set = pd.DataFrame(id_list, columns=["Tweet_id"])

    # Processing Tweet Data
    data_set["Tweet_full_text"] = [tweet.full_text for tweet in results]
    data_set["created_at"] = [tweet.created_at for tweet in results]
    data_set["retweet_count"] = [tweet.retweet_count for tweet in results]
    data_set["favorite_count"] = [tweet.favorite_count for tweet in results]
    data_set["source"] = [tweet.source for tweet in results]

    # Processing User Data
    data_set["user_id"] = [tweet.author.id for tweet in results]
    data_set["user_screen_name"] = [tweet.author.screen_name for tweet in results]
    data_set["user_name"] = [tweet.author.name for tweet in results]
    data_set["user_created_at"] = [tweet.author.created_at for tweet in results]
    data_set["user_description"] = [tweet.author.description for tweet in results]
    data_set["user_followers_count"] = [tweet.author.followers_count for tweet in results]
    data_set["user_friends_count"] = [tweet.author.friends_count for tweet in results]
    data_set["user_location"] = [tweet.author.location for tweet in results]
    data_set["Mark_num_tweets_recorded"] = [len(results) for tweet in results]
    data_set["Mark_Exchange_Rate"] = [exchange_rate for tweet in results]
    data_set["Mark_Timestamp"] = [data_time for tweet in results]

    return data_set

# Authentication procedure
auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
api = tweepy.API(auth)

# Open the file with the old tweet id, for use to obtain tweets since the last request
tweet_id_filename = "id_val.txt"
old_id_file = open(tweet_id_filename, 'r')
old_id = old_id_file.read()
old_id_file.close()

# The first entry in the results list is the latest tweet
# The language is filtered to english tweets
# The count value dictates the number of tweets returned
# The extra queries in the search field filter out retweets and replies as there are too many
results = api.search(q="brexit -filter:retweets -RT -filter:replies", lang="en", since_id=old_id, rpp=150, count=1500, tweet_mode='extended') # Example ID

# Reverse the list so the data can be added chronologically, with old data 1st
# and newest data last (at the bottom of the csv)
results.reverse()

# Tests
print(len(results))
cnt = 0

# Writing the new ID number to the file to read next batch of tweets since this number
tweet2 = results[-1]
data = str(tweet2.id)
tf = open(tweet_id_filename, 'w')
tf.write(data)
tf.close()
print_tweet(tweet2)

# Write the tweets out to the file
data_set = process_results(results)
data_set.to_csv('tweets_and_rates.csv', mode = 'a', index=False, header=None)
