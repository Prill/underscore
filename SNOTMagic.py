# Library that monitors the SNOT logs and takes action when certain actions
# happen.
# For example, you can have certain people or channels be notified whenever a
# ticket is flagged as UNIX. Or make have it alert people when a VIP0 ticket
# arrives. Or have it tell people when somebody assigned a ticket to them. The
# possibilities are endless

import CommandMonitoring as cm
import yaml, re, string
import snotparser.snotparser as sp
from twisted.internet import reactor
import smtplib
from email.mime.text import MIMEText

# Function that creates another function that is called with the contents of
# each line of the snot log.
def makeSNOTLogHandler(client):
    def handleSNOTLogLine(line):
        print line,
        regex = r"^(?P<date>.+?) CMD: (?P<cmd>\w+?) TKT: (?P<tkt>\d+?) BY: (?P<by>.+?)($| TO: (?P<to>.+))?$"
        match = re.match(regex, line)
        if match:
            try:
                mdict = match.groupdict()
                message = str(mdict)
                ticketDict = sp.parseTicket(int(mdict['tkt']), client.config['snot']['defaultCommand'])
                formattedTicket = sp.formatTicketDictSmart(ticketDict, client.config['snot']['formatString'])
                # "Case" statement for various ticket commands
                cmd = mdict["cmd"].lower()
                if cmd == "flags":
                    message = "#{tkt} (\"" + ticketDict['subject'] + "\") flagged as {to} by {by}"
                    message = message.format(**mdict)
                    if mdict['to'] in client.config['snot']['alerts']['flag']:
                        for target in client.config['snot']['alerts']['flag'][mdict['to']]:
                            client.notice(target, "Flagged as %s: %s" % (mdict['to'], formattedTicket))
                            client.logger.write("SNOTMagic: Message '%s' sent to %s" % (formattedTicket, string.join(client.config['snot']['alerts']['flag'][mdict['to']], ", ")) )
                    reactor.wakeUp()
                elif cmd == "recv":
                    client.msg(client.config['snot']['snot_channel'], "Received ticket #{tkt} from {by}".format(**mdict))
                    client.msg(client.config['snot']['snot_channel'], formattedTicket)
                    return
                elif cmd == "resp":
                    message = "{by} assigned #{tkt} to {to}".format(**mdict)
                elif cmd == "complete":
                    message = "#{tkt} completed by {by}".format(**mdict)
                elif cmd == "delete":
                    message = "#{tkt} deleted by {by}".format(**mdict)
                elif cmd == "update":
                    message = "#{tkt} (\"" + ticketDict['subject'] + "\") updated by {by}"
                    message = message.format(**mdict)
                elif cmd == "append":
                    message = "#{tkt} appended to #{to} by {by}".format(**mdict)
                elif cmd == "autoresolve":
                    message = "#{tkt} autoresolved - ({by})".format(**mdict)
                elif cmd == "priority" or cmd == "autopriority":
                    message = "#{tkt} priority set to {to} by {by}".format(**mdict)
                else:
                    message = line
                #client.logger.write("SNOTMagic: Message '%s' sent to %s" % (message, client.config['snot']['snot_channel']))
                client.msg(client.config['snot']['snot_channel'], message)
            except KeyError as ke:
                client.logger.write(str(ke))
                client.msg(client.config['snot']['snot_channel'], str(ke))
            except TypeError as te:
                client.logger.write(str(te))
                client.msg(client.config['snot']['snot_channel'], str(te))
        else:
            client.msg("#snot", "Could not match '%s'" % line)
        reactor.wakeUp()

    return handleSNOTLogLine

# Main function to be called in a subthread by the main program
def monitorLogs(client):
    cm.monitorFile(client.config['snot']['basedir'] + client.config['snot']['logFile'],
                   makeSNOTLogHandler(client))

def completeTicket(number, from_email, config, message=None):
    msg = MIMEText(message)
    msg['Subject'] = "Completing ticket #%d" % number
    msg['From']    = from_email
    msg['To']      = config['snot']['snotEmail']
    msg.add_header("X-TTS", "%d COMP" % number)

    s = smtplib.SMTP('localhost')
    s.sendmail(from_email, [msg['To']], msg.as_string())
    s.quit()

