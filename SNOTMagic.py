# Library that monitors the SNOT logs and takes action when certain actions
# happen.
# For example, you can have certain people or channels be notified whenever a
# ticket is flagged as UNIX. Or make have it alert people when a VIP0 ticket
# arrives. Or have it tell people when somebody assigned a ticket to them. The
# possibilities are endless

import CommandMonitoring as cm
import yaml

# Import YAML configuration. This should really be consolidated into one
# dictionary that can be accessed from multiple places. 
CONFIG_FILE = "config.yaml"
config = None
with open(CONFIG_FILE) as cfgFile:
    config = yaml.load(cfgFile)

# Main function to be called in a subthread by the main program
def monitorLogs(client):
   cm.monitorFile(config['snot']['basedir'] + "logs/log",
                    makeSNOTLogHandler(client))
