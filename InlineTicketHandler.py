import re
import snotparser.snotparser as sp
from datetime import datetime

def inlineTicketMatch(client, user, channel, msg):
    ticketNumbers = map(int, re.findall("#(\d{4,})", msg))
    # print ticketNumbers
    ticketMatch = re.search("#(\d{4,})", msg)
    if ticketNumbers:
        print datetime.today().strftime("%Y-%m-%d %H:%M:%S\t"), user, "requested ticket(s)", str(ticketNumbers), "in", channel
        for ticket in ticketNumbers:
            client.msg(channel, sp.formatTicket(ticket, "$number | $from_line | $assigned_to | $subject | $flags"))
