# -*- coding: utf-8 -*-
#
#  main.py
#  chives
#

import time
import os

import slackclient as sc


READ_WEBSOCKET_DELAY = 1

class STATES:
    class INIT:
        pass
    class NEED_WATER:
        pass
    class WATERED:
        pass
    class NOTUNDERSTOOD:
        pass


class Carrotina(object):
    def __init__(self, api_token, bot_name, bot_id):
        self.client = sc.SlackClient(api_token)
        self.bot_name = bot_name
        self.bot_id = bot_id
        self.state = STATES.INIT

    def loop(self):
        if self.client.rtm_connect():
            print("Bot connected and running!")
            while True:
                event_list = self.client.rtm_read()
                self.parse_slack_output(event_list)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

    def parse_slack_output(self, event_list):
        for event in event_list:
            print(event)
            if 'channel' in event and event.get('type') == 'message' and 'bot_id' not in event:
                channel = event['channel']
                text = event['text']
                if self.is_text_for_bot(text=text, channel_id=channel):
                    if self.state==STATES.INIT:
                        self.send_message(channel, text + str("... :smirk:  Well, I didn't drink anything today...")) #TODO select random
                        self.state=STATES.NEED_WATER
                    elif self.state==STATES.NEED_WATER:
                        if 'yes' not in text.lower().split():
                            self.send_message(channel, str("Thank you! I'm feeling goooood :leaves:"))
                            self.state=STATES.WATERED
                        else:
                            self.send_message(channel, str("Seems like you don't carrot-all :sweat_drops::scream: ... Will you water me? please"))
                            self.state=STATES.WATERED
                    elif self.state==STATES.WATERED:
                        if 'thirsty' in text.lower().split():
                            self.send_message(channel, str(" I'm kinda getting thirsty now :D "))
                            self.state=STATES.NEED_WATER
                        elif 'sleep' in text.lower().split():
                            self.send_message(channel, str("Good night honey :D "))
                            self.state=STATES.WATERED
                        elif 'feeling'in text.lower().split():
                            self.send_message(channel, str("I'm feeling awesome..."))
                            self.state=STATES.WATERED
                        else:
                            self.send_message(channel, str("I dont see what <"+text+"> means..."))
                            self.state=STATES.NOTUNDERSTOOD


                    elif self.state==STATES.NOTUNDERSTOOD:
                        self.send_message(channel, str("Ok now I'm getting thirsty again :scream: "))
                        self.state=STATES.NEED_WATER




    # checks whether the text or channel is for bot
    def is_text_for_bot(self, text, channel_id):
        return channel_id.startswith('D') or '<@{}>'.format(self.bot_id) in text

    def send_message(self, channel, response):
        self.client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)


def main():
    api_token = os.environ['CARROTINA_SLACK_TOKEN']
    bot_name = os.environ['CARROTINA_SLACK_NAME']
    bot_id = os.environ['CARROTINA_ID']

    bot = Carrotina(api_token, bot_name, bot_id)
    bot.loop()


if __name__ == '__main__':
    main()