"""
Little Bird

Description: Create custom notifications that display on phone and are read into
bluetooth headphones

Applications:
* Calendar reminder: "Meeting in 5min"
* Weather updates: "It's raining in Portland, OR"
* Smart home status: "Motion detected at home"
* News notifications in real-time: “Oregon stay at home order lifted"
* When a plant is dry: “Fiddle leaf fig soil is dry"

@source: https://realpython.com/twitter-bot-python-tweepy/
@source: https://www.geeksforgeeks.org/tweet-using-python/

Author: Nic La
Last modified: Sep 2020
"""

import tweepy
import logging
import threading
import time


# Configure logging
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")


def authenticate(consumer_key, consumer_secret, access_token, access_token_secret):
    """Authenticate to Twitter"""
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if api.verify_credentials():
        print("Authentication OK")
        return api
    else:
        print("Error during authentication")
        exit()


def send_dm(api, username, message):
    """
    Send direct message to specified user
    https://stackoverflow.com/questions/56726863/twitter-api-tweepy-library-send-direct-message
    """
    user = api.get_user(screen_name=username)

    event = {
      "event": {
        "type": "message_create",
        "message_create": {
          "target": {
            "recipient_id": user.id
          },
          "message_data": {
            "text": message
          }
        }
      }
    }

    # Send direct message
    api.send_direct_message_new(event)


def news_thread(delay):
    """Monitor Twitter news for keywords"""
    logging.info("News Thread: starting")
    time.sleep(delay)
    logging.info("News Thread: finishing")


def weather_thread(delay):
    """Monitor the weather for alerts"""
    logging.info("Weather Thread: starting")
    time.sleep(delay)
    logging.info("Weather Thread: finishing")


if __name__ == '__main__':
    # Pull tokens from file tokens.txt
    with open('tokens.txt') as tokens:
        CONSUMER_KEY = tokens.readline().strip()
        CONSUMER_SECRET = tokens.readline().strip()
        ACCESS_TOKEN = tokens.readline().strip()
        ACCESS_TOKEN_SECRET = tokens.readline().strip()

    # Authenticate to Twitter
    api_obj = authenticate(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # # Send Direct Message
    # username = 'sakeofmaking'
    # message = "Mauris tincidunt arcu odio, dignissim volutpat nibh rutrum non."
    # send_dm(api_obj, username, message)

    # Thread Loop
    MINUTE = 60
    HOUR = 3600
    x = threading.Thread(target=news_thread, args=(HOUR,))
    y = threading.Thread(target=weather_thread, args=(MINUTE*30,))
    while True:
        if not x.is_alive():
            x = threading.Thread(target=news_thread, args=(HOUR,))
            x.start()

        if not y.is_alive():
            y = threading.Thread(target=weather_thread, args=(MINUTE*30,))
            y.start()

        time.sleep(MINUTE)
        logging.info("Main    : all done")
