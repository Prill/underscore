import re
import snotparser.snotparser as sp
from datetime import datetime

def inlineTicketMatch(client, user, channel, msg):
    ticketMatch = re.search("#(\d{4,})", msg)
    if ticketMatch:
        print datetime.today().strftime("%Y-%m-%d %H:%M:%S\t"), user, "requested ticket", ticketMatch.group(1), "in", channel
        client.msg(channel, sp.formatTicket(int(ticketMatch.group(1)), "$number | $from_line | $assigned_to | $subject | $flags"))
