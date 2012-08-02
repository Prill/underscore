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
import argparse

# Local imports
import snotparser.snotparser as sp
import CommandHandler, InlineTicketHandler
from config import *

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

class UnderscoreBot(irc.IRCClient):
    """A logging IRC bot."""
    
    def __init__(self, autojoin, autojoin_list=DEFAULT_CHANNELS):
        self.autojoin_list = autojoin_list
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
        if self.autojoin:
            for channel, key in self.autojoin_list:
                self.join(channel, key)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        # Check to see if they're sending me a private message
        # TODO: This should be cleaned up to be less confusing in terms of channel vs user
        if channel == self.nickname:
			channel = user
		
                
        if (re.search("what day is it\?", msg)):
            self.msg(channel, UnderscoreBot.whatDay())
        InlineTicketHandler.inlineTicketMatch(self, user, channel, msg) 
        CommandHandler.handleCommand(self, user, channel, msg)

    def reloadModule(self, moduleName):
        module = sys.module[moduleName]
        if module:
            print "Reloading",moduleName
            reload(sys.modules[moduleName])
        else:
            print "No such module"
    
    def seeNames(self):
        return sys.modules
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
    
    def __init__(self, **kwargs):
        self.arguments = kwargs

    def buildProtocol(self, addr):
        p = UnderscoreBot(**self.arguments)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple IRC bot I wrote for theCAT")
    parser.add_argument("-n", "--no-autojoin", action="store_true")

    args = parser.parse_args()
    
    print "Initializing"
        
    # create factory protocol and application
    f = UnderscoreBotFactory(autojoin=not args.no_autojoin)

    # connect factory to this host and port
    reactor.connectSSL(DEFAULT_SERVER, 6697, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()
