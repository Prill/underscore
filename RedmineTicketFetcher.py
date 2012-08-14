# Library for fetching tickets from a redmine project using the REST API.
# Although primarily intended for use with our internal installation, I hope to
# make it as generic as possible.
# 
# I used this library as a base: http://code.google.com/p/pyredminews/
import urllib, urllib2
from shadow import chronicle
from xml.dom import minidom

#def fetchRedmineTicket(number
class RedmineTicketFetcher:
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def getTicket(self, number):
        requestURL = "%s/issues/%d.xml" % (self.url, number)
        request = urllib2.Request(requestURL)
        request.add_header("X-Redmine-API-Key", self.key)
        
        data = urllib2.urlopen(request)
        
        xmlObject = minidom.parse(data)

        issueNode = xmlObject.getElementsByTagName("issue")[0]
        d = {}
        for child in issueNode.childNodes:
            if child.hasChildNodes():
                d[child.nodeName] = child.firstChild.nodeValue
            elif child.hasAttributes():
                d[child.nodeName] = child.getAttribute("name")
        
        return d

if __name__ == "__main__":
    import sys
    rtf = RedmineTicketFetcher(chronicle.URL, chronicle.API_KEY)
    rtf.getTicket(int(sys.argv[1]))
