import re
import snotparser.snotparser as sp
from datetime import datetime
from string import Template
import string
import CommandHandler as ch
from RedmineTicketFetcher import RedmineTicketFetcher
from shadow import chronicle

class InlineTicketHandler:
    def __init__(self, url, key):
        self.rtf = RedmineTicketFetcher(chronicle.URL, chronicle.API_KEY)

def formatTicketList(ticketNumbers):
    formattedTickets = map(lambda l : string.join(l, "#"), ticketNumbers)
    return string.join(formattedTickets, ", ")

def inlineTicketMatch(client, user, channel, msg):
    #ticketNumbers = map(int, re.findall("#(\d{4,})", msg))
    

    ticketNumbers = re.findall("(\w+)?#(\d+)", msg)
    #print ticketNumbers
    if ticketNumbers:
        print datetime.today().strftime("%Y-%m-%d %H:%M:%S\t"), user, "requested ticket(s)", formatTicketList(ticketNumbers), "in", channel
        for ticket in ticketNumbers:
            ticketType = ticket[0].lower()
            if ticketType in ['','snot']:
                if int(ticket[1]) >= 1000:
                    client.msg(channel, sp.formatTicket(int(ticket[1]), "#$number (SNOT) | $from_line | $assigned_to | $subject | $flags"))
            elif ticketType in ['testsnot']:
                client.msg(channel, sp.formatTicket(int(ticket[1]), "#$number (TESTSNOT) | $from_line | $assigned_to | $subject | $flags", 'testsnot'))
            elif ticketType == 'c':
                try:
                    d = client.redmine_instance.getTicket(int(ticket[1]))
                    if d['project'] != "Mentor Sessions" or channel == "#mentors":
                        client.msg(channel, str(Template("#$id ($project) | $author | $assigned_to | $subject | $tracker").safe_substitute(d)))
                except Exception as e:
                    print "%s: %s" % (ticket[1], e)
                    client.msg(channel, "%s: %s" % (ticket[1], e))
            else:
                pass
            #    client.msg(channel, "Unrecognized ticket type '%s'" % ticket[0])
