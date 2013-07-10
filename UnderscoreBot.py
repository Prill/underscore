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
import SNOTMagic
import LibUnderscore

# from config import *
from shadow import chronicle
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
        #self.logger.addLogfile("raw", "raw.log")
        self.handlers = {}
        self.callbacks = []
        self.users = LibUnderscore.loadUserList()
        #self.addHandler(EasterEggHandler())
        for plugin in config['core']['plugins']['autoload']:
            self.addHandler(plugin[0], plugin[1])
    
    def addCallback(self, function):
        self.callbacks.append(function)
        print "Added callback: %s" % function

    def runCallbacks(self, *args):
        #print "Running callbacks with args %s" % (args,)
        self.callbacks[:] = [x for x in self.callbacks if not x(*args)]

    #        for callback in self.callbacks[event]:
    #            callback(*args)
    #        self.callbacks[event] = []

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger.write("Connection made")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.write("Connection lost")

    def lineReceived(self, line):
        #self.logger.write(" --> " + line, "raw", echo=False)
        irc.IRCClient.lineReceived(self, line)

    def sendLine(self, line):
        #self.logger.write(" <-- " + line, "raw", echo=False)
        irc.IRCClient.sendLine(self, line)
    
    def handleCommand(self, prefix, command, params):
        #print "handleCommand:"
        #print "\tprefix:", prefix
        #print "\tcommand:", command
        #print "\tparams:", params
        self.runCallbacks(prefix, command, params)
        irc.IRCClient.handleCommand(self, prefix, command, params)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.logger.write("Signed on")
        self.logger.write("Identifying to nickserv as %s" % (config['irc']['nick']))
        self.msg("nickserv", "identify %s %s" % (config["irc"]["nick"], config["irc"]["nickserv_password"]))
        if self.autojoin:
            for channel, key in self.autojoin_list:
                self.join(channel, key)
        self.logger.write("Nick is %s" % self.nickname)
        self.logger.write("Calling snot monitoring in subthread")
        reactor.callInThread(SNOTMagic.monitorLogs, self)

    def isAChannel(self,target):
        if len(target) > 0 and target[0] in ("#", "&", "+", "!"):
            return True;
        else:
            return False;

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        #self.mode("#wrentest2", True, "c");
        if msg == "modes?":
            def modesCallback(prefix, command, params):
                if prefix == "RPL_CHANNELMODEIS":
                    self.msg(channel, params[2])
                    return True
                elif prefix == "RPL_UMODEIS":
                    self.msg(channel, params[1])
                    return True
                return False
                #self.msg(channel, "The mode for %s is %s" % (rplChannel,rplModes))
                #return True
            self.addCallback(modesCallback)
            self.sendLine("MODE %s" % channel)

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
    def action(self, user, channel, data):
        nick = user.split('!', 1)[0]
        (username, host) = user.split('@', 1)

        for handler in self.handlers:
            if "action" in dir(self.handlers[handler]):
                self.handlers[handler].action(self, nick, channel, data)

    def reloadModule(self, moduleName):
        if moduleName in sys.modules:
            moduleObject = sys.modules[moduleName]
            reload(moduleObject)
            self.logger.write("Reloaded module " + str(moduleName))
            return "Reloading module " + str(moduleName)
        else:
            self.logger.write("Reload of %s failed; No such module" % moduleName)
            return "No such module"

    def reloadHandler(self, handlerName):
        if handlerName in self.handlers:
            handler = self.handlers[handlerName]
            handlerModuleName = handler.__module__
            self.reloadModule(handlerModuleName)
            self.handlers[handlerName] = getattr(sys.modules[handlerModuleName], handlerName)()
            self.logger.write("Reloaded handler " + str(handlerName))
            return "Reloaded handler " + str(handlerName)
        else:
            self.logger.write("Reload of %s failed; No such handler" % handlerName)
            return "No such handler"

    def addHandler(self, moduleName, handlerName):
        self.logger.write("Loading handler %s" % handlerName)
        try: 
            self.handlers[handlerName] = getattr(sys.modules[moduleName], handlerName)()
        except KeyError:
            self.logger.write("No such module: %s" % moduleName)
        except AttributeError:
            self.logger.write("No such attritube: %s.%s" % (moduleName, handlerName))
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
