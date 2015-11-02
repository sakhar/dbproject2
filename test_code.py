__author__ = 'sakhar'
import urllib2
import base64
import sys
import xml.etree.ElementTree as ET
# Just to test code (will not be submitted)

class Category:
    def __init__(self, name, parent):
        self.name = name
        self.queries = []
        self.subcats = {}
        self.docs = []
        self.matches = 0
        self.parent = parent

def parse_file(cat, file):
    f = open(file,'r')
    for line in f:
        entry = line.strip().split(' ')
        subcat = entry[0]
        query = entry[1:]
        try:
            cat.subcats[subcat.lower()]
        except:
            cat.subcats[subcat.lower()] = Category(subcat,cat)
        cat.subcats[subcat.lower()].queries.append(query)
        #cat.queries.append()

accountKey = 'XfbHf/vIn9YQOGFXSYwPnxOOmIWdeM95n39nD5s4FxI'
accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}

def get_matches(host, query):
    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=' \
          '%27site%3a' \
          +host+\
          '%20' \
          +'+'.join(query)+\
          '%27&$top=10&$format=Atom'
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    xml_root = ET.parse(response)
    entry = xml_root.find('{http://www.w3.org/2005/Atom}entry')
    content = entry.find('{http://www.w3.org/2005/Atom}content')
    properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
    total = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}WebTotal').text
    return int(total)

def print_subcats(root, i):
    try:
        name = root.parent.name
    except:
        name = '!'
    print i*'\t', root.name, name, root.queries
    #print (i+1)*'\t', root.queries
    for cat in root.subcats:
        print_subcats(root.subcats[cat],i+1)

def compute_ecoverage(cat):
    for query in cat.queries:
        cat.matches += get_matches(host, query)
    print cat.name, cat.matches
    for category in cat.subcats:
        compute_ecoverage(cat.subcats[category])



if __name__ == '__main__':
    t_es = 0
    t_ec = 0
    #host = 'fifa.com'
    host = 'fifa.com'
    query = 'premiership'
    '''try:
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
    '''
    'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=' \
    '%27site%3a' \
    'fifa.com%20premiership%27&$top=10&$format=Atom'



    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=' \
          '%27site%3a' \
          +host+\
          '%20' \
          +'+'.join(query.split(' '))+\
          '%27&$top=10&$format=Atom'


    #bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'\
    #              + '+'.join(query) + '%27&$top=10&$format=Atom'
    #url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3afifa.com%20premiership%27&$top=10&$format=Atom'
    #url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27site%3afifa.com%20premiership%27&$top=10&$format=Atom'
#    req = urllib2.Request(url, headers=headers)
#    response = urllib2.urlopen(req)
    #content = response.read()

#    root = ET.parse(response)

    #f = open('rr.xml','w')
    #f.write(content)
    #root = ET.parse('r.xml')
    #root = ET.parse(root)
    #

    #entry = root.find('{http://www.w3.org/2005/Atom}entry')
    #content = entry.find('{http://www.w3.org/2005/Atom}content')
    #properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
    #total = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}WebTotal').text
    #print total

    root = Category('Root', None)
    parse_file(root,'root.txt')
    for cat in root.subcats:
        parse_file(root.subcats[cat],cat+'.txt')
    #print_subcats(root,0)
    #for cat in root.subcats:
    #    print root.subcats[cat].queries
    compute_ecoverage(root)


