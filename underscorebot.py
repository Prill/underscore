from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl, task
from twisted.python import log

# system imports
import time, sys
from datetime import date
import re
import subprocess

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Braindump", "Saturday", "Sunday")

class UnderscoreBot(irc.IRCClient):
    nickname = "testbot"
    def connectionMade(self):
        lCheck = task.LoopingCall(self.checkLoggedIn)
        lCheck.start(10.0)
        irc.IRCClient.connectionMade(self)
    
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        self.join("#wrentest");
        #self.msg("#wrentest", "HA HA HA");


    def checkLoggedIn(self):
        print "Checking logged in users"
        self.scissorsUser = self.scissorsChecker.checkLoggedIn()
        if (self.scissorsUser):
            self.msg("#wrentest", "VOICE #hack %s" % self.scissorsUser)

    def __init__(self):
        print "Initializing UnderscoreBot"
        self.scissorsChecker = LinuxChecker()


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
    
        

class LinuxChecker:
    def checkLoggedIn(self):
        print "Checking LINUX"
        p = subprocess.Popen(['ssh','-T', '-i', '/home/wren/ubuntu/.ssh/unsecure_wren', '-o', 'HostbasedAuthentication=no', 'scissors'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #p = subprocess.Popen(['/u/wren/scripts/slowlist', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print "Received who data"
        # p = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            strippedLine = line.strip()
           # print strippedLine
           # return strippedLine
            userData = re.match(r"^(?P<username>\S+)\s.+\((?P<from>\S+)\)$", strippedLine)
            
            #print userData.group("username"), userData.group("from")
            if userData and userData.group("from") == "rita.cat.pdx.edu":
                print userData.group("username"), userData.group("from")
                return userData.group("username")
        else:
            return None

class SolarisChecker:
    def checkLoggedIn():
        print "HI"

if __name__ == '__main__':
    
    # create factory protocol and application
    f = UnderscoreFactory()
    
    # connect factory to this host and port
    reactor.connectSSL("irc.cat.pdx.edu", 6697, f, ssl.ClientContextFactory())
    # print reactor.getReaders()
    # print reactor.getWriters()
    # run bot
    reactor.run()
