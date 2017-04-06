from urllib.request import urlopen
from defines import STATS_URL

def stats_user_connected(username):
    url = "{}user?username={}&action=connected".format(STATS_URL, username)
    do_urlopen(url)

def stats_user_click(username, cat1, cat2=None):
    url = "{}click?username={}&cat1={}".format(STATS_URL, username, cat1)
    if cat2 != None:
        url += "&cat2={}".format(cat2)
    do_urlopen(url)

def do_urlopen(url):
    try:
        urllib.urlopen(url)
    except:
        print("urlopen() for url={} failed".format(url))
