#!/usr/bin/env python
# Basic module to load helper config
import yaml

helpFile = open('basichelp.yaml')
helpMessages = yaml.load(helpFile)

def getHelp(topic):
    return helpMessages[topic]
