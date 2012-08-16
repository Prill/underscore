# Handler class in which to put silly little Easter eggs that I add in.

import CommandHandler as ch

class EasterEggHandler:
    def privmsg(self, client, user, channel, msg):
        comm = ch.parseCommand(client.nickname, msg)
        print comm
        if comm["command"] == "herp":
            client.msg(channel, "derp")
