import re
import csv
import time
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Edge
# from msedge.selenium_tools import Edge, EdgeOptions

# Firefox
# from selenium import webdriver
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from webdriver_manager.firefox import GeckoDriverManager

# Chrome
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def get_tweet_data(card):
    """Extract data from tweet card"""
    username = card.find_element('xpath', './/span').text
#     print(username)
    try:
        handle = card.find_element('xpath', './/span[contains(text(), "@")]').text
    except NoSuchElementException:
        return
    
    try:
        postdate = card.find_element('xpath', './/time').get_attribute('datetime')
    except NoSuchElementException:
        return
    
#     comment = card.find_element('xpath', './/div[2]/div[2]/div[1]').text
#     responding = card.find_element('xpath', './/div[2]/div[2]/div[2]').text
    comment = card.find_element('xpath', './/div/div/div[2]/div[2]/div[2]').text

    text = comment.replace('\n', ' ') #+ responding

    # reply_cnt = card.find_element('xpath', './/div[@data-testid="reply"]').text
    # retweet_cnt = card.find_element('xpath', './/div[@data-testid="retweet"]').text
    # like_cnt = card.find_element('xpath', './/div[@data-testid="like"]').text
    
    # get a string of all emojis contained in the tweet
#     """Emojis are stored as images... so I convert the filename, which is stored as unicode, into 
#     the emoji character."""
#     emoji_tags = card.find_elements('xpath', './/img[contains(@src, "emoji")]')
#     emoji_list = []
#     for tag in emoji_tags:
#         filename = tag.get_attribute('src')
#         try:
#             emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
#         except AttributeError:
#             continue
#         if emoji:
#             emoji_list.append(emoji)
#     emojis = ' '.join(emoji_list)
#     text = text + ' ' + emojis
    
#     tweet = (username, handle, postdate, text, emojis, reply_cnt, retweet_cnt, like_cnt)
    tweet = (username, handle, postdate, text)
    return tweet

def get_driver(browser='Chrome'):
    # create instance of web driver

    # Edge
    # options = EdgeOptions()
    # options.use_chromium = True
    # driver = Edge(options=options)

    # Firefox
    # driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    # Chrome
    if browser == 'Chrome':
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    return driver

def twitter_login(user, handle, my_password, driver):
    # navigate to login screen
    driver.get('https://www.twitter.com/login')
    driver.maximize_window()
    sleep(5)
    username = driver.find_element('xpath', '//input[@name="text"]')
    username.send_keys(user)
    username.send_keys(Keys.RETURN)
    sleep(3)

    try:
        username = driver.find_element('xpath', '//input[@name="text"]')
        username.send_keys(handle)
        username.send_keys(Keys.RETURN)
        sleep(3)
    except:
        pass

    password = driver.find_element('xpath', '//input[@name="password"]')
    password.send_keys(my_password)
    password.send_keys(Keys.RETURN)
    sleep(10)
    return 

def perform_query(driver, keyword=None, hashtag=None, username=None, until_date=None, since_date=None, tweet_order='Latest'):
    query = ''
    if keyword is not None:
        query += '{}'.format(keyword)
    if hashtag is not None:
        if hashtag[0] == '#': query += ' ({})'.format(hashtag)
        else: query += ' (#{})'.format(hashtag)
    if username is not None:
        query += ' (from:{})'.format(username)
    query += ' lang:en'

    # if until_date is not None:
    #     query += ' until:{}'.format(until_date)
    # if since_date is not None:
    #     query += ' since:{}'.format(since_date)
    
    print('QUERY:', query)

    # find search input and search for term
    search_term = query
    search_input = driver.find_element('xpath', '//input[@aria-label="Search query"]')
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    sleep(1)

    # navigate to historical 'latest' tab
    if tweet_order == 'Latest':
        driver.find_element('link text', 'Latest').click()

def perform_scraping(driver, tweet_count=50):
    # get all tweets on the page
    start = time.time()

    data = []
    tweet_ids = set()
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True

    while scrolling:
        page_cards = driver.find_elements('xpath', '//*[@data-testid="tweet"]')
        for card in page_cards[-15:]:
            tweet = get_tweet_data(card)
            if tweet:
                tweet_id = ''.join(tweet)
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    data.append(tweet)
                
        scroll_attempt = 0
        while True:
            # check scroll position
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(5)
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1
                
                # end of scroll region
                if scroll_attempt >= 10:
                    scrolling = False
                    break
                else:
                    sleep(2) # attempt another scroll
            else:
                last_position = curr_position
                break
            
        if len(data) > tweet_count:
            print('Num tweets:', len(data))
            break
        
        print('scrolling:', scrolling)
    end = time.time()
    print('time taken: {:.2f}'.format(end - start))

    # Go to Home
    home = driver.find_element('xpath', '//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[1]')
    home.click()

    return data[:tweet_count]

# application variables
user = "username" #input('username: ')
handle = 'user_handle'
my_password = "password" #getpass('Password: ')
keyword = "IPL" #input('search term: ')

if __name__ == '__main__':
    # 1. Get driver
    driver = get_driver()
    # 2. Login
    twitter_login(user, handle, my_password, driver)
    # 3. Enter query
    perform_query(driver, keyword=keyword, hashtag=None, username=None, until_date=None, since_date=None, tweet_order='Latest')
    # 4. Scrape the data
    data = perform_scraping(driver, tweet_count=50)

    print(len(data))
    print([elem[-1] for elem in data])

    # 5. close the web driver
    driver.close()
