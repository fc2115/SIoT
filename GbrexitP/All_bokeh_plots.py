import pandas as pd
import numpy as np
from datetime import datetime
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from sklearn.preprocessing import MinMaxScaler
from scipy.signal import find_peaks
from textblob import TextBlob
import re
from sklearn.cross_validation  import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
from sklearn import tree, svm, ensemble

def exchangeRateRaw(data):
    p1 = figure(x_axis_type="datetime", plot_height = 250, sizing_mode="scale_width", tools='hover, pan, box_zoom, wheel_zoom, reset')
    p1.grid.grid_line_alpha=0.6
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Exchange Rate'
    p1.line(x=data.index.values, y=data['exchange_rate_mark'], color='#008080', line_width=1.2)
    p1.background_fill_alpha = 0
    p1.border_fill_alpha = 0
    p1.hover.tooltips = [
        ("Date and Time", "@x{%F %T}"),
        ("Euros to the Pound", "€@y{0.0000}")
        ]
    p1.hover.formatters = {
            'x': 'datetime'
        }
    p1.hover.mode = 'vline'
    return p1

def numTweetsRaw(data):
    p1 = figure(x_axis_type="datetime", plot_height = 250, sizing_mode="scale_width", tools='hover, pan, box_zoom, wheel_zoom, reset')
    p1.grid.grid_line_alpha=0.6
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Number of Tweets'
    p1.line(x=data.index.values, y=data['no_tweets_mark'], color='#800000', line_width=1.2)
    p1.background_fill_alpha = 0
    p1.border_fill_alpha = 0
    p1.hover.tooltips = [
        ("Date and Time", "@x{%F %T}"),
        ("No. Tweets featuring Brexit", "@y")
        ]
    p1.hover.formatters = {
            'x': 'datetime',
        }
    p1.hover.mode = 'vline'
    return p1

def tweetSentimentRaw(data):
    p1 = figure(x_axis_type="datetime", plot_height = 250, sizing_mode="scale_width", tools='pan, box_zoom, wheel_zoom, reset')
    p1.grid.grid_line_alpha=0.6
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Tweet Sentiment'
    p1.line(x=data.index.values, y=data['tweet_polarity'], color='#2d173c', legend='Raw Data', line_width=1)
    p1.legend.location = "top_left"
    p1.legend.click_policy="hide"
    p1.background_fill_alpha = 0
    p1.border_fill_alpha = 0

    # drop non numeric values
    reduced_df = data.drop(columns=['Tweet_id', 'Tweet_full_text', 'retweet_count', 'favorite_count', 'source', 'user_id', 'user_screen_name', 'user_name', 'user_created_at', 'user_description', 'user_followers_count', 'user_friends_count', 'user_location', 'timestamp_mark'])

    # resample for smoother curve viewing
    resample_period = '3T'
    downsampled_reduced_df = reduced_df.resample(resample_period).mean()

    # Complete the plot
    p1.line(x=downsampled_reduced_df.index.values, y=downsampled_reduced_df['tweet_polarity'], color='#FFC30B', legend='Downsampled Avg Data', line_width=1.2)

    return p1

def tweetRadicality(data):
    peaks, _ = find_peaks(data['tweet_polarity'], height=0.2)
    reduced_df = pd.DataFrame({'1': data.index.values[peaks], '2': data['tweet_polarity'][peaks]})
    reduced_df.set_index('1', inplace=True)

    resample_period = '3T'
    downsampled_reduced_df = reduced_df.resample(resample_period).sum()
    p1 = figure(x_axis_type="datetime", plot_height = 250, sizing_mode="scale_width", tools='pan, box_zoom, wheel_zoom, reset')
    p1.grid.grid_line_alpha=0.6
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Tweet Radicalness'
    p1.line(x=downsampled_reduced_df.index.values, y=downsampled_reduced_df['2'], color='#FFC30B', line_width=1.2)
    p1.background_fill_alpha = 0
    p1.border_fill_alpha = 0
    return p1

def normalizeData(column):
    # 3: Number of Tweets
    vals3 = column
    vals3 = vals3.values.reshape((len(vals3), 1))
    scaler3 = MinMaxScaler(feature_range=(0,1))
    scaler3 = scaler3.fit(vals3)
    normalized_vals_downsampled = scaler3.transform(vals3)

    # Remove lists within lists created by normalisation
    flat_list1 = [item for sublist in normalized_vals_downsampled for item in sublist]
    return flat_list1

def normalizeTweetData(data):
    # drop non numeric values
    reduced_df = data.drop(columns=['Tweet_id', 'Tweet_full_text', 'retweet_count', 'favorite_count', 'source', 'user_id', 'user_screen_name', 'user_name', 'user_created_at', 'user_description', 'user_followers_count', 'user_friends_count', 'user_location', 'timestamp_mark'])

    # resample for smoother curve viewing
    resample_period = '60T'
    downsampled_reduced_df = reduced_df.resample(resample_period).mean()
    downsampled_reduced_df_radicalness = reduced_df.resample(resample_period).sum()

    # normalize using the normalizeData() function
    normalized_num_tweets = normalizeData(downsampled_reduced_df['no_tweets_mark'])
    normalized_tweet_polarity = normalizeData(downsampled_reduced_df['tweet_polarity'])
    normalized_exchange_rate = normalizeData(downsampled_reduced_df['exchange_rate_mark'])
    normalized_tweet_radicalness = normalizeData(downsampled_reduced_df_radicalness['tweet_polarity'])
    dates = downsampled_reduced_df.index.values

    # plot the 3 lines
    p1 = figure(x_axis_type="datetime", sizing_mode="scale_width", plot_height = 250, tools='hover, pan, box_zoom, wheel_zoom, reset')
    p1.grid.grid_line_alpha=0.6
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Normalized Value'
    p1.line(x=dates, y=normalized_num_tweets, color='#4F4F4F', legend='Number of Tweets', line_width=2)
    p1.line(x=dates, y=normalized_tweet_radicalness, color='#FFC30B', legend='Tweet Radicalness', line_width=2)
    p1.line(x=dates, y=normalized_tweet_polarity, color='#2271B3', legend='Tweet Sentiment', line_width=3)
    p1.line(x=dates, y=normalized_exchange_rate, color='#33A02C', legend='Exchange Rate', line_width=4)
    p1.legend.location = "top_left"
    p1.legend.click_policy="hide"
    p1.background_fill_alpha = 0
    p1.border_fill_alpha = 0
    p1.hover.tooltips = [
        ("Date", "@x{%F %T}"),
        ("Value", "@y{0.000}")
        ]
    p1.hover.formatters = {
            'x': 'datetime',
            'y': 'numeral'
            }
    p1.hover.mode = 'vline'

    return p1

def autoCorr(input_data):
    maxLagDays = 8
    allTimeLags = np.arange(1,maxLagDays*24)

    # Normalise data, but not into a list this time
    vals3 = input_data
    vals3 = vals3.values.reshape((len(vals3), 1))
    scaler3 = MinMaxScaler(feature_range=(0,1))
    scaler3 = scaler3.fit(vals3)
    normalized_vals_downsampled = scaler3.transform(vals3)
    normalized_vals_downsampled_df = pd.DataFrame(normalized_vals_downsampled)

    data = normalized_vals_downsampled_df.iloc[:,0]
    auto_corr = [data.autocorr(lag=dt) for dt in allTimeLags]
    return auto_corr

def autoCorrTweetData(data):
    # drop non numeric values
    reduced_df = data.drop(columns=['Tweet_id', 'Tweet_full_text', 'retweet_count', 'favorite_count', 'source', 'user_id', 'user_screen_name', 'user_name', 'user_created_at', 'user_description', 'user_followers_count', 'user_friends_count', 'user_location', 'timestamp_mark'])

    # resample for smoother curve viewing
    resample_period = '60T'
    downsampled_reduced_df = reduced_df.resample(resample_period).mean()
    downsampled_reduced_df_radicalness = reduced_df.resample(resample_period).sum()

    maxLagDays = 8
    allTimeLags = np.arange(1,maxLagDays*24)

    autocorr_num_tweets = autoCorr(downsampled_reduced_df['no_tweets_mark'])
    autocorr_tweet_polarity = autoCorr(downsampled_reduced_df['tweet_polarity'])
    autocorr_exchange_rate = autoCorr(downsampled_reduced_df['exchange_rate_mark'])
    autocorr_tweet_radicalness = autoCorr(downsampled_reduced_df_radicalness['tweet_polarity'])

    p = figure(plot_height = 250, sizing_mode="scale_width", tools='hover, pan, box_zoom, wheel_zoom, reset')

    p.grid.grid_line_alpha=0.9
    p.xaxis.axis_label = 'Lags'
    p.yaxis.axis_label = 'Auto Correlation Value'
    p.line(x=allTimeLags, y=autocorr_num_tweets, color='#4F4F4F', line_width=2, legend='Number of Tweets Average Hourly')
    p.line(x=allTimeLags, y=autocorr_tweet_radicalness, color='#FFC30B', line_width=2, legend='Tweet Radicalness')
    p.line(x=allTimeLags, y=autocorr_tweet_polarity, color='#2271B3', line_width=3, legend='Tweet Sentiment')
    p.line(x=allTimeLags, y=autocorr_exchange_rate, color='#33A02C', line_width=4, legend='GBP EUR Exchange Rates')
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    p.legend.orientation = "horizontal"
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.hover.tooltips = [
        ("Lags", "@x"),
        ("Correlation", "@y{0.000}")
        ]
    p.hover.formatters = {
            'Lags'      : 'numeral', # use 'datetime' formatter for 'date' field
            'Correlation' : 'numeral',   # use 'printf' formatter for 'adj close' field
                                      # use default 'numeral' formatter for other fields
        }

    p.hover.mode = 'vline'
    return p

def clean_tweet(tweet):
    return ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def tweetSentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    if polarity > 0:
        feeling = 'positive'
    elif polarity == 0:
        feeling = 'neutral'
    elif polarity < 0:
        feeling = 'negative'

    return polarity, feeling

def exchangeRatePredictor(tweet, data):
    happy_val, feel = tweetSentiment(tweet)

    reduced_df = pd.DataFrame({'1': data.index.values, '2': data['tweet_polarity'], '3': data['exchange_rate_mark'], '4': data['no_tweets_mark']})
    reduced_df.set_index('1', inplace=True)

    # resample for smoother curve viewing
    resample_period = '10T'
    downsampled_reduced_df = reduced_df.resample(resample_period).mean()

    predictor = 'exchange'
    final_df = pd.DataFrame({'time': downsampled_reduced_df.index.values, 'polarity': downsampled_reduced_df['2'], 'exchange': downsampled_reduced_df['3']})
    final_df.set_index('time', inplace=True)

    scale_val = 10000

    x_df = scale_val*final_df.drop(columns=[predictor])
    y_df = scale_val*final_df[predictor]
    x_train, x_test, y_train, y_test = train_test_split(x_df,y_df,test_size=0.3, random_state=42)
    y_train=y_train.astype('int')
    x_train=x_train.astype('int')
    y_test=y_test.astype('int')
    x_test=x_test.astype('int')

    big_mac = tree.DecisionTreeClassifier(max_depth = 7)
    big_mac = big_mac.fit(x_train, y_train)

    print(x_test)

    return big_mac.predict(happy_val*10000)/10000, feel
