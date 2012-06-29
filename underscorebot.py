#!/usr/bin/env python

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl, task
from twisted.python import log

# system imports
import time, sys
from datetime import date

# local imports
from checkers import *

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Braindump", "Saturday", "Sunday")

class UnderscoreBot(irc.IRCClient):
    nickname = "testbot"
    currentUsers = []
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
    
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        self.join("#wrentest");
        lCheck = task.LoopingCall(self.checkLoggedIn)
        lCheck.start(10.0)
        self.msg("#wrentest", "HA HA HA");


    def checkLoggedIn(self):
        print "Checking logged in users"
        checkResults = []

        # Check scissors
        self.scissorsUser = self.scissorsChecker.checkLoggedIn()
        if (self.scissorsUser):
            checkResults.append(self.scissorsUser)

        # Check chandra
        self.chandraUser = self.chandraChecker.checkLoggedIn()
        if (self.chandraUser):
            checkResults.append(self.chandraUser)

        print "scissorsUser:", self.scissorsUser
        print "chandraUser:", self.chandraUser
        print checkResults

        # Put them into set form which allows us to do some pretty simple set operations
        currentSet = set(self.currentUsers)
        checkSet   = set(checkResults)
        print "currentSet:", currentSet
        print "checkSet:", checkSet

        print "checkSet - currentSet: ", checkSet - currentSet
        print "currentSet - checkSet: ", currentSet - checkSet

        for user in checkSet - currentSet:
            print "VOICE #hack %s" % user
            self.msg("#wrentest", "VOICE #hack %s" % user)
        for user in currentSet - checkSet:
            self.msg("#wrentest", "DEVOICE #hack %s" % user)

        self.currentUsers = checkResults;
        print self.currentUsers;
        # for user in checkResults:
        #     if user not in currentUsers:
        #         currentUsers.append(user)
        #         self.msg(channel, "VOICE #hack %s" % user)
        # for user in currentUsers:


        # Now time to check whether the list of users logged on has changed

    def __init__(self):
        print "Initializing UnderscoreBot"
        self.scissorsChecker = LinuxChecker('scissors')
        self.chandraChecker  = SolarisChecker('chandra', 3)


    #def privmsg(self, user, channel, msg):
        # self.msg(channel, "That's what you think")
        

class UnderscoreFactory(protocol.ClientFactory):
    """A factory for UnderscoreBots.
    A new protocol instance will be created each time we connect to the server.
    """
    # def __init__(self, channel, filename):
    #     self.channel = channel
    #     self.filename = filename

    #def __init__(self, linuxChecker):
    #    self.linuxChecker = linuxChecker

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
    # print reactor.getReaders()
    # print reactor.getWriters()
    # run bot
    reactor.run()
