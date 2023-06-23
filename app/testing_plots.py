import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
from PIL import Image
import os

result = {'Sentiment': '0.6',
          'Sarcasm': '0.4',
          'Combined': '0.51',
         }
# plt.ioff()
dpi = 400
fig, axs = plt.subplots(1, 3, figsize=(600 * (dpi/100) /dpi, 200* (dpi/100) /dpi), dpi=dpi)
fontdict = {'family':'cursive','color':'black','size':20}
for ax, classifier in zip(axs, result.keys()):
    patches, _, _ = ax.pie([float(result[classifier]), 1-float(result[classifier])], 
                            # labels=['Positive', 'Negative'],
                            colors=['#1DA1F2', 'red'],
                            autopct='%1.1f%%')
    
    ax.set_title(classifier, fontdict=fontdict)

fig.legend(patches, ['Positive', 'Negative'], loc='lower center', 
           ncols=2, 
           borderpad=0,
           frameon=False,
           framealpha=1.0
           )

plt.savefig('result_plot.png')


# text = ['Tweepy supports both OAuth 1a (application-user)', 'and OAuth 2 (application-only) authentication. Authentication is handled by the tweepy.AuthHandler class.']
# from wordcloud import WordCloud, STOPWORDS

# def create_wordcloud(text):
#     mask = np.array(Image.open(os.path.join('static', 'cloud2.png')))
#     stopwords = set(STOPWORDS)
#     wc = WordCloud(background_color='white',
#                    mask=mask, 
#                    max_words=3000, stopwords=stopwords, repeat=True)
#     wc.generate(str(text))
#     wc.to_file('wc.png')
#     print('Word Cloud Saved Successfully')

# create_wordcloud(text)