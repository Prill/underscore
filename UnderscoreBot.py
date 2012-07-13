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

# Local imports
import snotparser.snotparser as sp
from config import *

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Braindump", "Saturday", "Sunday")

class UnderscoreBot(irc.IRCClient):
    """A logging IRC bot."""
    
    def __init__(self, autojoin=DEFAULT_CHANNELS):
		self.autojoin = autojoin
    nickname = "_"
    
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
    @staticmethod
    def parseCommand(msg):
        command = re.match("^_:?\s*(?P<command>\S*)\s*(?P<args>.*)", msg)
        if command:
            return command.groupdict()
        else:
            return None

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        #self.msg(channel, "%s: " % (user,))
        #self.me(channel, "hugs %s" % (user,))
        #self.notice(channel, "Alert: %s said \"%s\"" % (user,msg))
        # Check to see if they're sending me a private message
        #if channel == self.nickname:
        #     msg = "It isn't nice to whisper!  Play nice with the group."
        #     self.msg(user, msg)
        #     return

        # Otherwise check to see if it is a message directed at me
        #if msg.startswith(self.nickname + ":join"):
        #    self.logger.log("<%s> %s" % (self.nickname, msg))
        if (re.search("what day is it\?", msg)):
            self.msg(channel, UnderscoreBot.whatDay())
        command = UnderscoreBot.parseCommand(msg)
        print command
        
        #helpCommand = re.match("^_:?\s*help\s*$", msg)
        #if helpCommand:
        
        if command:
            if command["command"] == "help":
                self.msg(channel,
                """Type `snot <ticketNumber>` to get the contents of a ticket.
    snot <ticketNumber> <formatString> to customize the output.
    Example: snot 171172 %(number)s | %(subject)s | %(assigned to)s | %(closing date)s""")

            elif command["command"] == "snot":
                snotCommand = re.match("\s*(?P<ticketNumber>\d+)\s*(?P<fString>.*)", command["args"])
                
                number = snotCommand.group("ticketNumber")
                fString = snotCommand.group("fString")

                if fString:
                    formattedString = sp.formatTicket(int(number), fString) 
                else:
                    formattedString = sp.formatTicket(int(number), "%(number)s | %(from_line)s | %(subject)s | (%(flags)s)")
                #self.msg(channel,"SNOT COMMAND TIME: %s" % snotCommand.groups("ticketNumber"))
                self.msg(channel, formattedString)

            elif command["command"] == "join":
                channeljoin = re.match("(#?\S*)\s*(.*)", command["args"])       
                # self.msg(channel, str(channeljoin.groups()))
                # for item in channeljoin.groups():
                #     self.msg(channel, item)
                chan = channeljoin.group(1)
                key  = channeljoin.group(2)
                if (key):
                    self.msg(channel, "Joining %s with key %s" % (chan, key)) 
                    self.join(chan, key)
                else:
                    self.msg(channel, "Joining %s (no key)" % (chan,))
                    self.join(chan)
			
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
    reactor.connectSSL("irc.cat.pdx.edu", 6697, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()
