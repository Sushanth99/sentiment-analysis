# page_cards = driver.find_elements('xpath', '//div[@data-testid="tweetText"]')
page_cards = driver.find_elements('xpath', '//article[@data-testid="tweet"]')
# page_cards = driver.find_elements('xpath', '//*[@id="id__2efnxrb40mb"]')

page_cards

card = page_cards[0]
username = card.find_element('xpath', './/div[@data-testid="User-Name"]')
tweet = card.find_element('xpath', './/div[@data-testid="tweetText"]')

print(username.text)

get_tweet_data(card)

card.find_element('xpath', './/span').text

tweet = card.find_elements('xpath', './/div/div/div[2]/div[2]/div[2]')
print(tweet)

''.join([elem.text for elem in tweet])

for card in page_cards[-15:]:
    tweet = get_tweet_data(card)
#     print(tweet)