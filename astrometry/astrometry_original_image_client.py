import re
import sys
import urllib2

HOST = 'http://35.202.61.141:8081'

def get_url(subid):
    url = '%s/user_images/%d' % (HOST, subid)
    resp = urllib2.urlopen(url)
    html = resp.read()

    m = re.search('"original": "/image/(\d+)', html)
    imageid = int(m.group(1))

    return '%s/image/%d' % (HOST, imageid)


if __name__ == '__main__':
    print get_url(int(sys.argv[1]))
