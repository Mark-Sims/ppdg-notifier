from pushbullet import PushBullet

apiKey = "<REDACTED>"

p = PushBullet(apiKey)

# Get a list of devices
devices = p.getDevices()

import os
import datetime
import urllib2
import json
import time
import pprint
from bs4 import BeautifulSoup

import socket
socket.setdefaulttimeout(25)

def get_deals():

    now = datetime.datetime.now()
    nextArchiveTime = now + datetime.timedelta(seconds=4)

    url = "http://stores.ebay.com/PP-Digital-Gifts/Discounts-Promotions-/_i.html?_fsub=7032965014&_sid=1243781594&_trksid=p4634.m322"
    deals = {}

    while True:
    
        now = datetime.datetime.now()
     
        html_str = ""
         
        try: 
            # Make the request 
                html = urllib2.urlopen(url)
                print "url opened"
                html_str = html.read()
                print "url read"

        except:
            pass
           
        # Use BeautifulSoup to parse it 
        soup = BeautifulSoup(html_str, 'html.parser')
        print "Souped"
        
        new_page_deals = set()
        
        for deal in soup.html.find(class_="tpgv"):
            if deal.get("class") == ["wp"]:
                details = deal.div.find_all(class_="title")[0].a
        
                text = details.contents[0]
                link = details.get('href')
        
            new_page_deals.add(text)
        
            if text not in deals:
                print "Found new deal: {}".format(text.encode('utf-8'))
                deals.update(
                    {
                    text : {
                        "link" : link,
                        "time" : str(now)
                    }
                    }
                )
                
                print "pushing" 
                p.pushNote(devices[0]["iden"], 'PPDG Alert', text)
                # Failsafe so I don't send unlimited push notifications accidentally
                time.sleep(10)
            
        to_delete = []
        for deal in deals:
            if deal not in new_page_deals:
                to_delete.append(deal)
        
        for deal in to_delete:
            print "Deal being dropped: {}".format(deal.encode('utf-8'))
            deals.pop(deal)
        
        
        # Archive the list once every 4 hours
        if now > nextArchiveTime:
            print "Archiving: {} > {}".format(now, nextArchiveTime)
        
            nextArchiveTime = now + datetime.timedelta(hours=1)
            archiveDir = now.strftime("%Y-%m-%d")

            if not os.path.exists(archiveDir):
                os.mkdir(archiveDir)
        
            archiveFile = os.path.join(archiveDir, now.strftime("%H-%M-%S"))

            print "file opened" 
            with open(archiveFile, 'w') as arch:
                json.dump(deals, arch)
        
        else:
            print "Not archiving: {} > {}".format(now, nextArchiveTime)
        
        time.sleep(30)

    
    

from mock import patch, Mock

# First HTML has deals  A,B,C,D,E,F
# Second HTML has deals A,C,E,G,H,I,J,K,L

# Therefore, upon processing the 2nd request, we should pick up 
# deals G,H,I,J,K,L, and then drop deals B,D,F
@patch('urllib2.urlopen')
def test_get_deals_1(mock_urllib2_open):

    with open("deals_6.html", "r") as six:
        html_6 = six.read()
    
    with open("deals_9.html", "r") as six:
        html_9 = six.read()

    mock_return = Mock()
    mock_return.read.side_effect = [html_6, html_9]

    mock_urllib2_open.return_value = mock_return

    get_deals()


# First HTML has deals A,C,E,G,H,I,J,K,L
# Second HTML has deals  A,B,C,D,E,F

# Therefore, upon processing the 2nd request, we should pick up 
# deals B,D,F and then drop deals G,H,I,J,K,L
@patch('urllib2.urlopen')
def test_get_deals_2(mock_urllib2_open):

    with open("deals_6.html", "r") as six:
        html_6 = six.read()
    
    with open("deals_9.html", "r") as six:
        html_9 = six.read()

    mock_return = Mock()
    mock_return.read.side_effect = [html_9, html_6]

    mock_urllib2_open.return_value = mock_return

    get_deals()


#test_get_deals_1()
#test_get_deals_2()

get_deals()

