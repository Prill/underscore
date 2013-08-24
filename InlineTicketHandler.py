import re
import snotparser.snotparser as sp
from datetime import datetime
from string import Template
import string
import CommandHandler as ch
from RedmineTicketFetcher import RedmineTicketFetcher
from shadow import chronicle
from UnderscoreBot import config

class InlineTicketHandler:
    def privmsg(self, client, user, channel, msg):
        inlineTicketMatch(client, user, channel, msg)
    def action(self, client, nick, channel, msg):
        inlineTicketMatch(client, nick, channel, msg)

def formatTicketList(ticketNumbers):
    formattedTickets = map(lambda l : string.join(l, "#"), ticketNumbers)
    return string.join(formattedTickets, ", ")

def inlineTicketMatch(client, user, channel, msg):
    ticketNumbers = re.findall("(\w+)?#(\d+)", msg)
    #print ticketNumbers
    if ticketNumbers:
        client.logger.write("%s requested ticket(s) %s in %s" % (user, formatTicketList(ticketNumbers), channel))
        for ticket in ticketNumbers:
            ticketType = ticket[0].lower()
            if ticketType in ['','snot','tts']:
                if int(ticket[1]) >= config['snot']['minimumInline']:
                    client.msg(channel, sp.formatTicketSmart(int(ticket[1]), config['snot']['formatString'], config['snot']['defaultCommand']))
                    # client.msg(channel, sp.formatTicket(int(ticket[1]), "$number (SNOT) | $from_line | $assigned_to | $subject | $flags"))
            elif ticketType in ['testsnot']:
                client.msg(channel, sp.formatTicket(int(ticket[1]), "$number (TESTSNOT) | $from_line | $assigned_to | $subject | $flags", 'testsnot'))
            elif ticketType == 'c':
                try:
                    d = client.redmine_instance.getTicket(int(ticket[1]))
                    if d['project'] != "Mentor Sessions" or channel == "#mentors":
                        client.msg(channel, str(Template("$id ($project) | $author | $assigned_to | $subject | $tracker").safe_substitute(d)))
                except Exception as e:
                    print "%s: %s" % (ticket[1], e)
                    client.msg(channel, "%s: %s" % (ticket[1], e))
            else:
                pass
            #    client.msg(channel, "Unrecognized ticket type '%s'" % ticket[0])
