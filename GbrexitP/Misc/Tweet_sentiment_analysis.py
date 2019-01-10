import pandas as pd
from textblob import TextBlob
import re
import csv

def clean_tweet(tweet):
    return ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


df = pd.read_csv('tweets_and_rates.csv')
print(len(df))
feature_names = df.columns[0:-1].values.tolist()

with open('Tweet_sentiment.csv','w',newline='') as fd:
    count = 0
    for tweet in range(len(df)):
        try:
            analysis = TextBlob(clean_tweet(df['Tweet_full_text'][count]))
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            if polarity > 0:
                feeling = 'positive'
            elif polarity == 0:
                feeling = 'neutral'
            elif polarity < 0:
                feeling = 'negative'
            myCsvRow = [polarity, subjectivity, feeling]

        except TypeError:
            myCsvRow = []
            print("Null Row Written at")
            print(count)

        writer = csv.writer(fd)
        writer.writerow(myCsvRow)
        count = count + 1


# Checking how many positive and how many negative total
df = pd.read_csv('Tweet_sentiment.csv')
print(len(df))
feature_names = df.columns[0:-1].values.tolist()

positive = df['tweet_sentiment'].isin(['positive'])
# print(df[positive])
print(len(df[positive]))

negative = df['tweet_sentiment'].isin(['negative'])
# print(df[negative])
print(len(df[negative]))

neutral = df['tweet_sentiment'].isin(['neutral'])
# print(df[neutral])
print(len(df[neutral]))
