from urllib.request import urlopen
from defines import STATS_URL

def stats_user_connected(username):
    url = "{}user?username={}&action=connected".format(STATS_URL, username)
    do_urlopen(url)

def stats_user_click(username, cat1, cat2=None):
    url = "{}click?username={}&cat1={}".format(STATS_URL, username, cat1)
    if cat2:
        url += "&cat2={}".format(cat2)
    do_urlopen(url)

def do_urlopen(url):
    try:
        resp = urlopen(url)
        return resp
    except:
        print("urlopen() for url={} failed".format(url))
        return None

sent_msg = 0
def update_sent_msg():
    global sent_msg
    sent_msg += 1
    print('sent_msg={}'.format(sent_msg))

drop_msg = 0
def update_drop_msg():
    global drop_msg
    drop_msg += 1
    print('drop_msg={}'.format(drop_msg))
