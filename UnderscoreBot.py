#!/usr/bin/python
"""
    Miscellaneous bot
"""


# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

# system imports
import time, sys
from datetime import date
import re
import yaml

# Local imports
import snotparser.snotparser as sp
import CommandHandler
from config import *

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

class UnderscoreBot(irc.IRCClient):
    """A logging IRC bot."""
    
    def __init__(self, autojoin=DEFAULT_CHANNELS):
		self.autojoin = autojoin
    nickname = PREFERRED_NICK
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.msg("nickserv", "identify %s" % NICKSERV_PASSWORD)
        for channel, key in self.autojoin:
            self.join(channel, key)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
			channel = user
		
        ticketMatch = re.search("#(\d{4,})", msg)
        if ticketMatch:
            print ticketMatch.group(1)
            self.msg(channel, sp.formatTicket(int(ticketMatch.group(1)), "%(number)s | %(summary_email)s | %(assigned to)s | %(subject)s | (%(flags)s)"))

        if (re.search("what day is it\?", msg)):
            self.msg(channel, UnderscoreBot.whatDay())
        CommandHandler.handleCommand(self, user, channel, msg)

        
    # irc callbacks

    def names(self, channel):
        "List the users in 'channel', usage: client.who('#testroom')"
        self.sendLine('WHO %s' % channel)

    def irc_RPL_WHOREPLY(self, *nargs):
        "Receive WHO reply from server"
        print 'NAMES:' , nargs

    @staticmethod
    def whatDay():
        currentDay = date.today().weekday()
        return """It's %(today)s, %(today)s, gotten get down on %(today)s! (Yesterday was %(yesterday)s, %(yesterday)s! Today it is %(today)s! We, we so excited, we gonna have a ball today! Tomorrow is %(tomorrow)s, and %(dayAfterTomorrow)s comes afterwaaaaard!)""" % \
                  {"yesterday": DAYS[(currentDay - 1) % 7], \
                   "today": DAYS[(currentDay) % 7], \
                   "tomorrow": DAYS[(currentDay + 1) % 7], \
                   "dayAfterTomorrow": DAYS[(currentDay + 2) % 7]}


class UnderscoreBotFactory(protocol.ClientFactory):
    """A factory for UnderscoreBots.

    A new protocol instance will be created each time we connect to the server.
    """

    #def __init__(self):

    def buildProtocol(self, addr):
        p = UnderscoreBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    print "Initializing"
    
    # create factory protocol and application
    f = UnderscoreBotFactory()

    # connect factory to this host and port
    reactor.connectSSL(DEFAULT_SERVER, 6697, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()
