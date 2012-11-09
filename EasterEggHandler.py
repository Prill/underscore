# Handler class in which to put silly little Easter eggs that I add in.

import CommandHandler as ch
import re
from datetime import date

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

def whatDay():
    currentDay = date.today().weekday()
    return """It's %(today)s, %(today)s, gotta get down on %(today)s! (Yesterday was %(yesterday)s, %(yesterday)s! Today it is %(today)s! We, we so excited, we gonna have a ball today! Tomorrow is %(tomorrow)s, and %(dayAfterTomorrow)s comes afterwaaaaard!)""" % \
              {"yesterday": DAYS[(currentDay - 1) % 7], \
               "today": DAYS[(currentDay) % 7], \
               "tomorrow": DAYS[(currentDay + 1) % 7], \
               "dayAfterTomorrow": DAYS[(currentDay + 2) % 7]}

class EasterEggHandler:
    def privmsg(self, client, user, channel, msg):
        print "Hello %s" % channel
        client.msg(channel, "Hello %s" % channel)
        comm = ch.parseCommand(client.nickname, msg)
        if comm:
            print comm
            if comm["command"] == "herp":
                client.msg(channel, "derp")
        
        elif (re.search("what day is it\?", msg)):
            client.msg(channel, whatDay())

