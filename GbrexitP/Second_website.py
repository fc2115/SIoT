from flask import Flask, render_template, url_for, request
import pandas as pd
import numpy as np
from datetime import datetime
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from sklearn.preprocessing import MinMaxScaler
from bokeh.models import ColumnDataSource
from scipy.signal import find_peaks
import All_bokeh_plots
app = Flask(__name__)

# # Load the Tweets_and_Rates CSV Data File
df = pd.read_csv('tweets_and_rates.csv')
feature_names = df.columns[0:-1].values.tolist()

# Clean up the data
df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce', dayfirst=True)
df = df.dropna(subset=['created_at', 'exchange_rate_mark', 'tweet_polarity']) # This is working! Just the index 61821 is removed!
df.set_index('created_at', inplace=True)
# Begin Web Application
@app.route("/", methods=['GET', 'POST'])
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/raw")
def raw():
    plotExchangeRate = All_bokeh_plots.exchangeRateRaw(df)
    scriptE, divE = components(plotExchangeRate)

    plotNumTweets = All_bokeh_plots.numTweetsRaw(df)
    scriptN, divN = components(plotNumTweets)

    plotTweetSentiment = All_bokeh_plots.tweetSentimentRaw(df)
    scriptS, divS = components(plotTweetSentiment)

    plotTweetRadicality = All_bokeh_plots.tweetRadicality(df)
    scriptR, divR = components(plotTweetRadicality)

    return render_template('raw.html', title='Home', scriptE=scriptE, divE=divE, scriptN=scriptN, divN=divN, scriptS=scriptS, divS=divS, scriptR=scriptR, divR=divR)

@app.route("/analysis")
def analysis():
    plotAllNormalized = All_bokeh_plots.normalizeTweetData(df)
    scriptA, divA = components(plotAllNormalized)

    plotAllAutoCorr = All_bokeh_plots.autoCorrTweetData(df)
    scriptC, divC = components(plotAllAutoCorr)

    return render_template('analysis.html', title='About', scriptA=scriptA, divA=divA, scriptC=scriptC, divC=divC)

@app.route("/predictions", methods=['GET', 'POST'])
def predictions():
    return render_template('predictions.html')

@app.route("/result", methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        result = request.form['text']
        exchange_rate, tweet_feel = All_bokeh_plots.exchangeRatePredictor(tweet=result, data=df)
        return render_template("result.html", exchange_rate=exchange_rate, tweet_feel=tweet_feel, result=result)

@app.route("/insights")
def insights():
    return render_template('insights.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
