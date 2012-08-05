#!/usr/bin/env python
# Basic module to load helper config
import yaml

#helpFile = open('basichelp.yaml')
helpFile = open('help.yaml')
helpMessages = yaml.load(helpFile)

def getHelp(topic=None):
    if not topic:
        topicString = "Topics: "
        for t in helpMessages:
            topicString += t + " "
        return topicString
    else:
        return helpMessages[topic]

def getHelp2(topic):
    if not topic:
        return getHelp2("about")
    else:
        helpBase = helpMessages[topic]
        messages = [helpBase["topic"]]
        if "subtopics" in helpBase and helpBase["subtopics"] != None:
            subtopics = "Subtopics:"
            for subt in helpBase["subtopics"]:
                subtopics += subt + " "
            messages.append(subtopics)
        return messages

