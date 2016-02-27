# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from urlparse import parse_qs, urlparse
import redis
import settings
import sys
import time
import twitter
import urllib2


r = redis.StrictRedis(host='localhost', port=6379, db=0)
api = twitter.Api(consumer_key=settings.CONSUMER_KEY,
    consumer_secret=settings.CONSUMER_SECRET,
    access_token_key=settings.ACCESS_TOKEN_KEY,
    access_token_secret=settings.ACCESS_TOKEN_SECRET)
print api.VerifyCredentials()

url = "http://www.inven.co.kr/board/powerbbs.php?come_idx="
tip_url = url + "17"

last_tip_l = int(r.get('tip_id'))

try:
  data = urllib2.urlopen(tip_url).read().decode("euc-kr", "replace").encode("utf-8")
  soup = BeautifulSoup(data)
  items = soup.findAll('td', {'class':'bbsSubject'} )

  idx_list = []

  for i in items:
    if i.previousSibling.find('img') is None:
      a = i.find('a', {})['href']

      #p = int(a[-5:])
      p = int(parse_qs(urlparse(a).query, keep_blank_values=True)[u'l'][0])

      if last_tip_l >= p:
        break
      else:
        print p
        idx_list.insert(0, p)

  for item in idx_list:
    article = tip_url + "&l=" + str(item)
    print article
    data = urllib2.urlopen(article).read()
    soup = BeautifulSoup(data)
    items = soup.findAll('h1', {})
    print items[0].contents[0]
    api.PostUpdate(items[0].contents[0] + " " + article)

  if len(idx_list) > 0:
    last_tip_l = idx_list[-1]
    r.set('tip_id', idx_list[-1])

except urllib2.URLError:
  #TODO: find out a cause of this error, maybe caused by frequent request or robots.txt
  print "URL ERROR OCCURED"

sys.stdout.flush()
sys.stderr.flush()
