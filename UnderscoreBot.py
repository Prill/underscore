#!/usr/bin/python
"""
    Miscellaneous bot
"""
print __file__

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
from shadow import chronicle
from redmine import *
from RedmineTicketFetcher import RedmineTicketFetcher
from EasterEggHandler import EasterEggHandler

CONFIG_FILE = "config.yaml"
config = None
with open(CONFIG_FILE) as cfgFile:
    config = yaml.load(cfgFile)

class UnderscoreBot(irc.IRCClient):
    """A logging IRC bot."""
    
    def __init__(self, autojoin, autojoin_list=config["irc"]["channels"], nick=config["irc"]["nick"]):
        self.autojoin_list = autojoin_list
        self.autojoin = autojoin
        self.nickname = nick
        self.handlers = {}
        self.redmine_instance = RedmineTicketFetcher(config["redmine"]["url"], config["redmine"]["api_key"])
        self.addHandler(EasterEggHandler())

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
        print "Nick is", self.nickname
 
    def privmsg(self, user, channel, msg):
         
        # Check to see if they're sending me a private message
        # TODO: This should be cleaned up to be less confusing in terms of channel vs user
        if channel == self.nickname:
			channel = user

        print "Handling PRIVMSG"
        for alias,handler in self.handlers.iteritems():
            if "privmsg" in dir(handler):
                print "\tRunning %s.privmsg" % handler
                handler.privmsg(self, user, channel, msg)
        # CommandHandler.handleCommand(self, user, channel, msg)
        

    def reloadModule(self, moduleName):
        if moduleName in sys.modules:
            moduleObject = sys.modules[moduleName]
            reload(moduleObject)
            return "Reloading " + str(moduleName)
        else:
            return "No such module"
    
    def addHandler(self, handler, alias=None):
        if alias == None:
            alias = type(handler)
        self.handlers[alias] = handler
    
    def deleteHandler(self, alias):
        del d[alias]

    def seeNames(self):
        return sys.modules
    # irc callbacks

    def names(self, channel):
        "List the users in 'channel', usage: client.who('#testroom')"
        self.sendLine('WHO %s' % channel)

    def irc_RPL_WHOREPLY(self, *nargs):
        "Receive WHO reply from server"
        print 'NAMES:' , nargs

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
    parser.add_argument("-a", "--no-autojoin", action="store_true", help="Do not autojoin channels upon connecting")
    parser.add_argument("-n", "--nick", action="store", help="Default nick upon joining", default=config["irc"]["nick"])
    args = parser.parse_args()
    
    print "Initializing"
    print __file__
    # create factory protocol and application
    f = UnderscoreBotFactory(autojoin=not args.no_autojoin, nick=args.nick)

    # connect factory to this host and port
    reactor.connectSSL(DEFAULT_SERVER, 6697, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()
