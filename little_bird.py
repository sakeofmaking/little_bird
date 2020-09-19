#!/usr/bin/env python3

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
@source: https://github.com/chubin/wttr.in

Author: Nic La
Last modified: Sep 2020
"""

import tweepy
import logging
import threading
import time
import re
import subprocess
import os
import sys


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


def news_thread(delay, api):
    """Monitor Twitter news for keywords"""
    logging.info("News Thread: starting")

    # Poll @BBCBreaking for latest tweet
    timeline = api.user_timeline(id="BBCBreaking")
    tweets = []
    pattern = r"^(.*)(https.*)"
    for tweet in timeline:
        result = re.search(pattern, f"{tweet.user.name}: {tweet.text}")
        if result:
            tweets.append(result[1].strip())

    # Compare tweets with past tweets
    past_tweets = []
    with open("news_log.txt") as news_log:
        for line in news_log:
            past_tweets.append(line.strip())
    try:
        if tweets[0] != past_tweets[0]:
            send_dm(api, "sakeofmaking", tweets[0])
            logging.info("News direct message sent")
    except IndexError:
        logging.info("No past tweets logged")

    # Update news log
    with open("news_log.txt", "w") as news_log:
        news_log.writelines(tweet + "\n" for tweet in tweets)

    time.sleep(delay)

    logging.info("News Thread: finishing")


def weather_thread(delay, api):
    """Monitor the weather for alerts"""
    logging.info("Weather Thread: starting")

    # Use curl wttr.in to poll weather for precipitation
    pattern = r"^(.*),.*: (.*)"
    precipitation = subprocess.check_output(r'curl wttr.in?format="%l:+%p\n"', shell=True).decode("utf-8")
    result = re.search(pattern, precipitation)
    if result:
        precipitation = f"{result[2]} of rain in {result[1]}"

    # Compare current precipitation with past precipitation
    with open("weather_log.txt") as weather_log:
        past_precipitation = weather_log.readline()
    if precipitation > past_precipitation:
        send_dm(api, "sakeofmaking", precipitation)
        logging.info("Weather direct message sent")

    # Update weather log
    with open("weather_log.txt", "w") as weather_log:
        weather_log.write(precipitation)

    time.sleep(delay)
    logging.info("Weather Thread: finishing")


def clear_thread(delay, api):
    """Clears terminal of text"""
    logging.info("Clear Thread: starting")

    # Check platform
    if sys.platform == 'win32':
        # Windows command clear
        os.system('cls')
    else:
        # Linux shell clear
        os.system('clear')

    time.sleep(delay)
    logging.info("Clear Thread: finishing")


if __name__ == '__main__':
    # Pull tokens from file tokens.txt
    with open('tokens.txt') as tokens:
        CONSUMER_KEY = tokens.readline().strip()
        CONSUMER_SECRET = tokens.readline().strip()
        ACCESS_TOKEN = tokens.readline().strip()
        ACCESS_TOKEN_SECRET = tokens.readline().strip()

    # Authenticate to Twitter
    api_obj = authenticate(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Thread Loop
    MINUTE = 60
    HOUR = 3600
    x = threading.Thread(target=clear_thread, args=(HOUR*24, api_obj))
    y = threading.Thread(target=news_thread, args=(HOUR, api_obj))
    z = threading.Thread(target=weather_thread, args=(MINUTE*30, api_obj))
    while True:
        if not x.is_alive():
            x = threading.Thread(target=clear_thread, args=(HOUR*24, api_obj))
            x.start()

        if not y.is_alive():
            y = threading.Thread(target=news_thread, args=(HOUR, api_obj))
            y.start()

        if not z.is_alive():
            z = threading.Thread(target=weather_thread, args=(MINUTE*30, api_obj))
            z.start()

        time.sleep(MINUTE)
        logging.info("Main    : all done")
