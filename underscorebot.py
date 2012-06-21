from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

# system imports
import time, sys
from datetime import date
import re

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Braindump", "Saturday", "Sunday")

class UnderscoreBot(irc.IRCClient):
    nickname = "_"
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
    
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        self.join("#wrentest");
        #self.msg("#wrentest", "HA HA HA");

    def privmsg(self, user, channel, msg):
        self.msg(channel, "That's what you think");


class UnderscoreFactory(protocol.ClientFactory):
    """A factory for UnderscoreBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # def __init__(self, channel, filename):
    #     self.channel = channel
    #     self.filename = filename
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
    
    # create factory protocol and application
    f = UnderscoreFactory()

    # connect factory to this host and port
    reactor.connectSSL("irc.cat.pdx.edu", 6697, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()
