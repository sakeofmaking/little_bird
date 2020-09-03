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


# Authenticate to Twitter
with open('tokens.txt') as tokens:
    CONSUMER_KEY = tokens.readline().strip()
    CONSUMER_SECRET = tokens.readline().strip()
    ACCESS_TOKEN = tokens.readline().strip()
    ACCESS_TOKEN_SECRET = tokens.readline().strip()
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# api.update_status("Test to see if notifications are working")
# api.send_direct_message(recipient_id='sakeofmaking', text='versation')
# https://stackoverflow.com/questions/56726863/twitter-api-tweepy-library-send-direct-message

user = api.get_user(screen_name='sakeofmaking')

event = {
  "event": {
    "type": "message_create",
    "message_create": {
      "target": {
        "recipient_id": user.id
      },
      "message_data": {
        "text": "This is a Twitter notification"
      }
    }
  }
}

# Send direct message
api.send_direct_message_new(event)

# if __name__ == '__main__':
#     print('Test')

