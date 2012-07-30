import re
import snotparser.snotparser as sp

def parseCommand(prefix, msg):
    command = re.match("^" + prefix + ":?\s*(?P<command>\S*)\s*(?P<args>.*)", msg)
    if command:
        return command.groupdict()
    else:
        return None

def handleCommand(client, user, channel, msg): 
    command = parseCommand(client.nickname, msg)
     
    if command:
        print channel, user + "\t%(command)s: %(args)s" % command
        if command["command"] == "help":
            client.msg(channel,
            """Type `snot <ticketNumber>` to get the contents of a ticket.
snot <ticketNumber> <formatString> to customize the output.
Example: snot 171172 %(number)s | %(subject)s | %(assigned to)s | %(closing date)s""")
        elif command["command"] == "snot":
            snotCommand = re.match("\s*#?(?P<ticketNumber>\d+)\s*(?P<fString>.*)", command["args"])
            
            number = snotCommand.group("ticketNumber")
            fString = snotCommand.group("fString")

            if fString:
                formattedString = sp.formatTicket(int(number), fString) 
            else:
                formattedString = sp.formatTicket(int(number), "%(number)s | %(summary_email)s | %(assigned to)s | %(subject)s | (%(flags)s)") 
            #client.msg(channel,"SNOT COMMAND TIME: %s" % snotCommand.groups("ticketNumber"))
            client.msg(channel, formattedString)

        elif command["command"] == "join":
            channeljoin = re.match("(#?\S*)\s*(.*)", command["args"])       
            # client.msg(channel, str(channeljoin.groups()))
            # for item in channeljoin.groups():
            #     client.msg(channel, item)
            chan = channeljoin.group(1)
            key  = channeljoin.group(2)
            if (key):
                client.msg(channel, "Joining %s with key %s" % (chan, key)) 
                client.join(chan, key)
            else:
                client.msg(channel, "Joining %s (no key)" % (chan,))
                client.join(chan)

        elif command["command"] == "part":
            channelPart = re.match("(#?\S*)\s*", command["args"])       
            client.leave(channelPart.group(1), "Parting is such sweet sorrow")

        elif command["command"] == "reload":
            client.reloadModule("CommandHandler")
        
        elif command["command"] == "dir":
            client.msg(channel, str(client.seeNames()))
        
        elif command["command"] == "herp":
            client.msg(channel, "derpina")
			
