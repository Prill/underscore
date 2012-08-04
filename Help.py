#!/usr/bin/env python
# Basic module to load helper config
import yaml

helpFile = open('basichelp.yaml')
helpMessages = yaml.load(helpFile)

def getHelp(topic=None):
    if not topic:
        topicString = "Topics: "
        for t in helpMessages:
            topicString += t + " "
        return topicString
    else:
        return helpMessages[topic]
