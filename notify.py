from google.appengine.api import urlfetch
from google.appengine.api import mail
import datetime
from google.appengine.ext import db

class AvailabilityStatus(db.Model):
    seen_at = db.DateTimeProperty(auto_now_add=True)
    available = db.BooleanProperty()

def fetchPlayLinks():
    url = "http://web.playmobile.pl/resources/flash/telefony/linki.csv"
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        return result.content
    else:
        return None
    
def getHeroLine(content):
    for line in content.splitlines():
        if 'htchero' in line: return line
    return None

def isHeroAvailable(line):
    parts = [str for str in line.split(';') if str]
    return len(parts) > 2

def availabilityChanged(state):
    last = db.GqlQuery("SELECT * FROM AvailabilityStatus ORDER BY seen_at DESC LIMIT 1")
    
    for previousStatus in last:
        if previousStatus.available == state: return False

    return True

def storeAvailability(availability):
    status = AvailabilityStatus(available = availability)
    status.put()

def sendNotification(available):
    txt = 'no longer'
    if available: txt = 'now'
    mail.send_mail(sender="Hero Notifier <onethater@gmail.com>",
              to="apoh@orange.pl",
              subject="HTC Hero is "+txt+" available in Play e-shop",
              body="HTC Hero is "+txt+" available in Play e-shop", 
              cc='adam@pohorecki.pl')
    
def main():
    print 'Content-Type: text/plain'
    print ''
    content = fetchPlayLinks()
    if not content:
        print 'could not fetch content' 
        return
    line = getHeroLine(content)
    if not line:
        print 'could not find hero line' 
        return
    available = isHeroAvailable(line)
    if availabilityChanged(available):
        sendNotification(available)
    storeAvailability(available)
    if available:        
        print 'available'
    else:
        print 'not available'

if __name__ == '__main__':
    main()