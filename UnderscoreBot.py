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
from Logger import Logger

# from config import *
from shadow import chronicle
from redmine import *
from RedmineTicketFetcher import RedmineTicketFetcher
import EasterEggHandler

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
        self.redmine_instance = RedmineTicketFetcher(config["redmine"]["url"], config["redmine"]["api_key"])
        self.logger = Logger("main.log")

        self.handlers = {}
        #self.addHandler(EasterEggHandler())
        for plugin in config['core']['plugins']['autoload']:
            self.addHandler(plugin[0], plugin[1])

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger("Connection made")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.msg("nickserv", "identify %s" % config["irc"]["nickserv_password"])
        if self.autojoin:
            for channel, key in self.autojoin_list:
                self.join(channel, key)
        print "Nick is", self.nickname

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        # Check to see if they're sending me a private message
        # TODO: This should be cleaned up to be less confusing in terms of channel vs user
        if channel == self.nickname:
			channel = user
        
        CommandHandler.handleCommand(self, user, channel, msg)
        #print "Handlers:", self.handlers
        for handler in self.handlers:
            #print handler, dir(handler)
            if "privmsg" in dir(self.handlers[handler]):
                self.handlers[handler].privmsg(self, user, channel, msg)

    def reloadModule(self, moduleName):
        if moduleName in sys.modules:
            moduleObject = sys.modules[moduleName]
            reload(moduleObject)
            return "Reloading " + str(moduleName)
        else:
            return "No such module"

    def reloadHandler(self, handlerName):
        if handlerName in self.handlers:
            handler = self.handlers[handlerName]
            handlerModuleName = handler.__module__
            self.reloadModule(handlerModuleName)
            self.handlers[handlerName] = getattr(sys.modules[handlerModuleName], handlerName)()
            return "Reloading" + str(handlerName)
        else:
            return "No such handler"

    def addHandler(self, moduleName, handlerName):
        print "Loading handler", handlerName
        print getattr(sys.modules[moduleName], handlerName)()

        self.handlers[handlerName] = getattr(sys.modules[moduleName], handlerName)()

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
    reactor.connectSSL(config["irc"]["server"], 6697, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()
