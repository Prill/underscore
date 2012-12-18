import re
import snotparser.snotparser as sp
from datetime import datetime
from string import Template
import string
import CommandHandler as ch
from RedmineTicketFetcher import RedmineTicketFetcher
from shadow import chronicle

class InlineTicketHandler:
    def privmsg(self, client, user, channel, msg):
        inlineTicketMatch(client, user, channel, msg)

def formatTicketList(ticketNumbers):
    formattedTickets = map(lambda l : string.join(l, "#"), ticketNumbers)
    return string.join(formattedTickets, ", ")

def formatTicketString(ticketDict, formatString): 
    # formatString will be in the form of "assigned_to,from_line,subject" csv
    formatKeys = formatString.split(',')
    formattedItems = []
    for key in formatKeys:
        key = key.strip()
        if key == "from":
            from_line = ticketDict["from_line"]
            print from_line
            emailRegex = '\s?(?P<email>(?P<username>\S+?)@(?P<domain>\S+?))\s?'
            m = re.match(r"^%s(\s.*)?$" % emailRegex, from_line) or re.match(r'^\s*?"?(?P<name>.+?)"? \<%s\>' % emailRegex, from_line)
            print m.groupdict()
            if m:
                md = m.groupdict()
                emailFormatted = md["email"]
                if re.match("(cat|cecs|ece|ee|cs|etm|me|mme|cee|ce)\.pdx\.edu", md["domain"]):
                    emailFormatted = md["username"]
                
                itemText = ""
                if "name" in md:
                    formattedItems.append("%s (%s)" % (md["name"], emailFormatted))
                else:
                    formattedItems.append(emailFormatted)
            else:
                formattedItems.append("ERROR (yell at Wren)")
        else:
            if key in ticketDict and ticketDict[key].strip():
                formattedItems.append(ticketDict[key])
    return string.join(formattedItems, " | ")

def inlineTicketMatch(client, user, channel, msg):
    ticketNumbers = re.findall("(\w+)?#(\d+)", msg)
    #print ticketNumbers
    if ticketNumbers:
        client.logger.write("%s requested ticket(s) %s in %s" % (user, formatTicketList(ticketNumbers), channel))
        for ticket in ticketNumbers:
            ticketType = ticket[0].lower()
            if ticketType in ['','snot']:
                if int(ticket[1]) >= 1000:
                    client.msg(channel, formatTicketString(sp.parseTicket(int(ticket[1])), "number, from, assigned_to, subject, flags"))
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
