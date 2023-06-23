import emoji
import snscrape.modules.twitter as sntwitter

import os
import sys
import re
import pickle
import json

import numpy as np
import tensorflow as tf 
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences 

from flask import session
from functools import wraps

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
from PIL import Image

def check_logged_in(func: object) -> object:
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'logged_in' in session:
			return func(*args, **kwargs)
		return 'You are NOT logged in.'

	return wrapper

def check_login():
     if 'logged_in' in session:
          return True
     return False

class TSAClassifier:
    def __init__(self, model_path, tokenizer_path, max_length=35, print_summary=False):
        self.model = tf.keras.models.load_model(model_path)
        with open(tokenizer_path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)
        if print_summary == True:
            self.model.summary()
        self.max_length = max_length
    
    def predict(self, input_sentences, round_results=True):
        input_sentences = self.clean_sentences(input_sentences)
        sequences = self.tokenizer.texts_to_sequences(input_sentences)
        padded_sequences = pad_sequences(sequences, maxlen=self.max_length)
        if round_results:
                return np.round(self.model.predict(padded_sequences))#.tolist()
        return self.model.predict(padded_sequences)#.tolist()
    
    @staticmethod
    def clean_sentences(sentences):
        # preprocessing
        # 1. Removing links
        pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        sentences = [re.sub(pattern, r' ', tweet) for tweet in sentences]
        # 2. Removing numbers
        sentences = [re.sub(r'\d+', r'', tweet) for tweet in sentences]
        # 3. Replacing hastags and emojis with words and removing punctuation
        sentences = [re.sub(r'[_:.]', r' ', emoji.demojize(re.sub(r'#(\w+)\b', r'\1', sentence))) for sentence in sentences]
        sentences = [re.sub(r'[^\w\s]', '', tweet) for tweet in sentences]
        # 4. Removing handles
        sentences = [re.sub(r'@[a-z0-9_]{1,15}', r'', tweet) for tweet in sentences]
        # 5. lowercasing 
        sentences = [sentence.lower() for sentence in sentences]
        # 6. Contracting elongated words
        sentences = [re.sub(r'(.)\1{2,}', r'\1', tweet) for tweet in sentences]
        # 7. Expanding contractions
        sentences = [contractions.fix(tweet) for tweet in sentences]
        # 8. Removing all extra spaces
        sentences = [' '.join(tweet.split()) for tweet in sentences]
        return sentences

def load_model():
    model_path = os.path.join(os.getcwd(), 'saved_model', 'sentiment_model')
    tokenizer_path = os.path.join(os.getcwd(), 'saved_model', 'sentiment_tokenizer.pickle')

    sentiment_model = TSAClassifier(model_path, tokenizer_path, max_length=35)

    model_path = os.path.join(os.getcwd(), 'saved_model', 'sarcasm_model')
    tokenizer_path = os.path.join(os.getcwd(), 'saved_model', 'sarcasm_tokenizer.pickle')

    sarcasm_model = TSAClassifier(model_path, tokenizer_path, max_length=35)

    return sentiment_model, sarcasm_model


def get_tweets(keyword=None, hashtag=None, username=None, tweet_count=100, until_date=None, since_date=None):
    print('Getting Twitter Data...')
    # query = 'Good Morning "Good Afternoon" (Good OR Evening) -Good -Night (#WonderfulDay) (from:ANI) lang:en until:2023-03-31 since:2023-03-18'
    query = ''
    if keyword is not None:
        query += '{}'.format(keyword)
    if hashtag is not None:
        if hashtag[0] == '#': query += ' ({})'.format(hashtag)
        else: query += ' (#{})'.format(hashtag)
    if username is not None:
        query += ' (from:{})'.format(username)
    query += ' lang:en'
    # print('UNTIL DATE:',until_date, len(until_date))
    # print('SINCE DATE:', since_date, len(since_date))
    # if until_date is not None:
    #     query += ' until:{}'.format(until_date)
    # if since_date is not None:
    #     query += ' since:{}'.format(since_date)
    
    print('QUERY:', query)
    # query = '{} lang:en'.format(keyword)

    tweet_list = []
    meta_data = []
    _input_data = {}
    counter = 1
    for tweet in sntwitter.TwitterSearchScraper(query).get_items():
        meta_data.append([tweet.date, tweet.id, tweet.rawContent, tweet.user.username, tweet.url])
        tweet_list.append(tweet.rawContent.lower())
        _input_data[tweet.id] = tweet.url
        counter += 1
        if counter > tweet_count:
            break
    
    # with open('_input_data.json', 'w') as f:
    #     json.dump(_input_data, f)
    _input_data = json.dumps(_input_data)
    print(len(tweet_list))
    return tweet_list, _input_data

from tweets_from_selenium import *
driver = get_driver()
twitter_login(user, handle, my_password, driver)
def get_tweets_using_selenium(keyword=None, hashtag=None, username=None, tweet_count=100, until_date=None, since_date=None):
     # 1. Get driver
    # driver = get_driver()
    # 2. Login
    # twitter_login(user, handle, my_password, driver)
    # 3. Enter query
    perform_query(driver, keyword=keyword, hashtag=hashtag, username=username, until_date=until_date, since_date=since_date, tweet_order='Top')
    # 4. Scrape the data
    data = perform_scraping(driver, tweet_count=tweet_count)

    tweet_list = [elem[-1].lower() for elem in data]
    print(len(data))
    # print(tweet_list)

    # 5. close the web driver
    # driver.close()
    return tweet_list, data
    



def nlp(analysis_type, text, classifier, tweet_count, until_date, since_date, sentiment_model, sarcasm_model):
    
    #1. Scrape Tweets
    # SINGLE TWEET
    if analysis_type == 'single_tweet':
        tweet_list, _input_data = [text], [text]

    # BY USERNAME
    elif analysis_type == 'by_username':
        tweet_list, _input_data = get_tweets_using_selenium(username=text, tweet_count=tweet_count, until_date=until_date, since_date=since_date)

    # BY KEYWORD
    elif analysis_type == 'by_keyword':
        tweet_list, _input_data = get_tweets_using_selenium(keyword=text, tweet_count=tweet_count, until_date=until_date, since_date=since_date)

    else:
        return None
    
    #2. Perform Analysis
    # Removing links
    # pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    # tweet_list = [re.sub(pattern, r' ', tweet) for tweet in tweet_list]

    sentiment_preds = np.squeeze(sentiment_model.predict(tweet_list, round_results=True))
    sarcasm_preds = np.squeeze(sarcasm_model.predict(tweet_list, round_results=True))
    if sentiment_preds.shape == ():
        sentiment_preds, sarcasm_preds = [int(sentiment_preds)], [int(sarcasm_preds)]
        # combined_preds = sentiment_preds ^ sarcasm_preds
    combined_preds = np.array([int(i)^int(j) for i, j in zip(sentiment_preds, sarcasm_preds)])
    result = {'Sentiment': '{:.2f}'.format(np.sum(sentiment_preds)/len(sentiment_preds)),
              'Sarcasm': '{:.2f}'.format(np.sum(sarcasm_preds)/len(sarcasm_preds)),
              'Combined': '{:.2f}'.format(np.sum(combined_preds)/len(combined_preds)),
             }
    
    print('After the result')
    positive_tweet_list = [tweet for tweet, pred in zip(tweet_list, combined_preds) if int(pred)==1]
    negative_tweet_list = [tweet for tweet, pred in zip(tweet_list, combined_preds) if int(pred)==0]

    
    get_plots(result)
    print('After getting the plots')

    create_wordcloud(tweet_list, title='wc_all')
    # create_wordcloud(positive_tweet_list, title='wc_pos')
    # create_wordcloud(negative_tweet_list, title='wc_neg')
    print('After creating wordcloud')
    #3. Return results
    return result, _input_data


# plotting results
def get_plots(result):
    plt.style.use('ggplot')
    dpi = 600
    fig, axs = plt.subplots(1, 3, figsize=(600 * (dpi/100) /dpi, 200* (dpi/100) /dpi), dpi=dpi)
    fontdict = {'color': 'black','size': 8}
    for ax, classifier in zip(axs, result.keys()):
        patches, _, _ = ax.pie([float(result[classifier]), 1-float(result[classifier])], 
                                # labels=['Positive', 'Negative'],
                                colors=['#7fcdfd94', '#d3d3d3'],
                                textprops={'fontsize': 8},
                                autopct='%1.1f%%')
        
        ax.set_title(classifier, fontdict=fontdict)

    fig.legend(patches, ['Positive', 'Negative'], loc='lower center', 
            ncols=2,
            fontsize=8, 
            borderpad=0,
            frameon=False,
            framealpha=1.0
            )
    plt.savefig(os.path.join('static', 'result_plot.png'))

    return None

def create_wordcloud(text, title):
    mask = np.array(Image.open(os.path.join('static', 'cloud2.png')))
    stopwords = set(STOPWORDS)
    wc = WordCloud(background_color='white', width=700, height=670,
                   
                   max_words=3000, stopwords=stopwords, repeat=True)
    wc.generate(str(text).lower())
    wc.to_file(os.path.join('static', '{}.png'.format(title)))
    # print('Word Cloud Saved Successfully')