# <CommandMonitoring.py>
# Generic interface library for monitoring commands for new lines. Calls a 
# user-specified method whenever a new line is added to the file.

import subprocess

# Monitors a specific file and calls function(line) for every new line that is
# written to the end. Currently implemented as a special case of monitorCommand
# using `tail -f` to watch the file.
def monitorFile(filepath, function):
    pass

# Monitor the output of a command and called function(line) with each new line
# of output the command generates.
def monitorCommand(command, args, function):
    pass
