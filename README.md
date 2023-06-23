# Twitter Sentiment Analysis

### About
The web application performs sentiment analysis of a topic of interest on twitter using Deep Learning model. The analysis performs two kinds of classifications:

1. Tone: positive or negative? (Model 1)
2. Sarcasm: Is sarcastic or not? (Model 2)

### Model
The application uses two models with LSTM-CNN architecture built using TensorFlow and [GloVe vectors](https://nlp.stanford.edu/projects/glove/) for word embeddings. The data for Model 1 is taken from [Tweet Sentiment Extraction dataset](https://www.kaggle.com/competitions/tweet-sentiment-extraction/overview) and for Model 2 from [News Headlines Dataset For Sarcasm Detection](https://www.kaggle.com/datasets/rmisra/news-headlines-dataset-for-sarcasm-detection). The models architecture is available in the ```twitter_sentiment_analysis_abridged.ipynb``` file.

### Implementation
The application is built using the Flask web framework and MySQL database. Users can enter a keyword and choose the time period and number of tweets for analysis. By default, the application analyses the latest 100 tweets containing the keyword. In addition to that, users can also use twitter's advanced search tool to get more specific queries. 

Users can register with a username and password for saving their queries and result history.

The application initially leveraged snscrape twitter-search endpoint before Twitter closed access to third party APIs. The application still works with individual user accounts using Selenium for scraping the tweets.

### Future Scope
Though both these models have close to 90 percent accuracy on the evaluation dataset, this can be improved by using a more advanced LSTM model or a Transformer model. The scraping of tweet using Selenium is slow and therefore the recommended implementation would be to use the official Twitter API. The analysis can also be extended to more sentiments and other social media applications. Building a front-end real-time dashboard would allow interested users to track sentiments of various trends and topics. Commercially, companies can track public online opinion of their brand or product.

