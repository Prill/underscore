from twisted.internet import reactor

def checkAuthStatus(client, nick, authenticatedFunction,
                                   noSuchNickFunction,
                                   notAuthenticatedFunction):
    def callback(prefix, command, params):
        if prefix == "330" and params[1].lower() == nick.lower() and authenticatedFunction:
            #client.msg(channel, "%s is logged in as %s" % (params[1], params[2]))
            authenticatedFunction(params[1], params[2])
            return True
        elif prefix == "ERR_NOSUCHNICK" and params[1].lower() == nick.lower() and noSuchNickFunction:
            #client.msg(channel, "%s does not appear to be a current user" % (params[1]))
            noSuchNickFunction(params[1])
            return True
        elif prefix == "RPL_ENDOFWHOIS" and params[1].lower() == nick.lower() and notAuthenticatedFunction:
            #client.msg(channel, "%s does not appear to be logged in." % (params[1]))
            notAuthenticatedFunction(params[1])
            return True
        else:
            return False
    client.addCallback(callback)
    client.sendLine("WHOIS %s" % nick)

def loadUserList():
    users = {}
    f = open('shadow/nick-account_map');
    for line in f:
        nick,account = line.strip().split(',')
        users[nick] = account
    return users
