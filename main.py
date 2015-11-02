'''
Columbia University
COMS E6111 Advanced Database Systems, Fall 2015
Project 2

Students:
Robert Dadashi-Tazehozi, UNI: rd2669
Sakhar Alkhereyf       , UNI: sa3147

'''
import sys
import base64
import xml.etree.ElementTree as ET
import urllib2
import base64

accountKey = 'XfbHf/vIn9YQOGFXSYwPnxOOmIWdeM95n39nD5s4FxI'
accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}


class Category:
    def __init__(self, name, parent):
        self.name = name
        self.queries = []
        self.subcats = {}
        self.docs = []
        self.parent = parent
        self.ecoverage = 0
        self.especificity = 0

def parse_file(cat, file):
    f = open(file, 'r')
    for line in f:
        entry = line.strip().split(' ')
        subcat = entry[0]
        query = entry[1:]
        try:
            cat.subcats[subcat.lower()]
        except:
            cat.subcats[subcat.lower()] = Category(subcat, cat)
        cat.subcats[subcat.lower()].queries.append(query)


def get_matches(host, query):
    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=' \
          '%27site%3a' \
          + host + \
          '%20' \
          + '+'.join(query) + \
          '%27&$top=10&$format=Atom'
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    xml_root = ET.parse(response)
    entry = xml_root.find('{http://www.w3.org/2005/Atom}entry')
    content = entry.find('{http://www.w3.org/2005/Atom}content')
    properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
    total = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}WebTotal').text
    return int(total)


def compute_ecoverage(cat):
    for query in cat.queries:
        cat.ecoverage += get_matches(host, query)
    print cat.name, cat.matches
    for category in cat.subcats:
        compute_ecoverage(cat.subcats[category])


if __name__ == "__main__":
    try:
        t_es = float(sys.argv[1])
        t_ec = int(sys.argv[2])
        host = sys.argv[3]

        if t_es > 1 or t_es < 0:
            raise Exception()
        if t_ec < 1:
            raise Exception()
    except:
        print 'Usage: python main.py <t_es> <t_ec> <host>'
        print 'example: python main.py 0.6 100 health.com'

    t_es = 0
    t_ec = 0
    # host = 'fifa.com'
    host = 'fifa.com'
    query = 'premiership'

    root = Category('Root')
    parse_file(root, 'root.txt')
    for cat in root.subcats:
        parse_file(root.subcats[cat], cat + '.txt')

    compute_ecoverage(root)
