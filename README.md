# SIoT - Felix Crowther
## !!! Important !!!
The data File was too large (>25mb) to be stored here, so I have inluded its link here:  
https://drive.google.com/open?id=14t7piWnjWSlbWVpJpCtsDH-6ukN7EiZp  

This file should be saved to the root directory of GbrexitP  

The 'Misc' Directory contains various programs not used in the final website application, but were used along the way make some permanent changes, i.e. tweet sentiment analysis.

## Auto_sense_store
This directory contains all the code used to automatically collect the data. The server used was a raspberry pi, and as such, instead of running the program in a continuous for loop (which, in case of an error could cause big holes in the data), it was run on the RPi linux scheduler, using crontab. The 'Data Mining' script was run once every 3 minutes (therefore gathering data once every 3 minutes), and the 'G sheets upload' script run hourly to backup the data to goole drive.  
#### Extra Python Packages Required
- tweepy==3.7.0  
- gspread==3.1.0  
- oauth2client==4.1.3   
- requests==2.11.1   

## GbrexitP
This directory contains the full working codes to run the local host web server application. Provided the csv data file 'tweets_and_rates.csv' is downloaded to the root (in GbrexitP), one need only run the 'Second_website.py' script, and navigate to the local host address stated in the console, where the webApp should be fully functional.
#### Extra Python Packages Required
- flask==0.11.1  
- datetime==4.3   
- bokeh==1.0.3  
- sklearn==0.17.1   
- scipy==1.2.0  
- textblob==0.15.2  
