import re
import snotparser.snotparser as sp

def inlineTicketMatch(client, user, channel, msg):
    ticketMatch = re.search("#(\d{4,})", msg)
    if ticketMatch:
        print user, "requested ticket", ticketMatch.group(1), "in", channel
        client.msg(channel, sp.formatTicket(int(ticketMatch.group(1)), "$number | $summary_email | $assigned_to | $subject | $flags"))
