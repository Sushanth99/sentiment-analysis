#!/usr/bin/env python3
from flask import Flask, render_template, request
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
import json
import datetime
from utilities import * 

## Versions
print('Python version:', sys.version)
print('NumPy version:', np.__version__)
# print('Pandas version:', pd.__version__)
print('TensorFlow version:', tf.__version__)


sentiment_model, sarcasm_model = load_model()

# Variables
timestamp = datetime.datetime.today().strftime('%d-%m-%Y %H:%M:%S')

# Getting data from form
analysis_type = 'by_keyword' #request.form.get('analysis_type', None)
# text = 'Good Morning Everyone. how are you all doing?' #request.form.get('tweet', None)
text = 'Covid'
classifier = 'Both' #request.form.get('classifier', None)
tweet_count = 100 #request.form.get('tweet_count', None)
since_date = None #request.form.get('since_date', None)
until_date = None #request.form.get('until_date', None)

# res = {'sentiment': sentiment_model.predict([text]),
#        'sarcasm': sarcasm_model.predict([text])}
# res = json.dumps(res)
# tweet_list, _input_data = get_tweets(keyword=text, hashtag=None, username=None, tweet_count=tweet_count, until_date=None, since_date=None)
# print(len(tweet_list))
res, _input_data = nlp(analysis_type, text, classifier, tweet_count, until_date, since_date, sentiment_model, sarcasm_model)

print(res)