'''
Columbia University
COMS E6111 Advanced Database Systems, Fall 2015
Project 2

Students:
Robert Dadashi-Tazehozi, UNI: rd2669
Sakhar Alkhereyf       , UNI: sa3147

'''
import sys
import urllib2
import base64
import sys
import xml.etree.ElementTree as ET
import pickle

accountKey = 'XfbHf/vIn9YQOGFXSYwPnxOOmIWdeM95n39nD5s4FxI'
accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}

class Category:
    def __init__(self, name, parent):
        self.name = name
        self.queries = []
        self.subcats = {}
        self.docs = []
        self.matches = 0
        self.parent = parent
        self.especi = 0


def compute_especificity(cat):
    if cat.name == 'Root':
        cat.especi = 1
    else:
        parent_sum = 0
        for category in cat.parent.subcats:
            parent_sum += cat.parent.subcats[category].matches
        parent_spec = cat.parent.especi
        cat.especi = float(parent_spec*cat.matches)/parent_sum
        print 'Specificity for category:', cat.name, ' is:', cat.especi
        print 'Coverage for category: ', cat.name, 'is:', cat.matches
    if cat.especi < t_es or cat.matches < t_ec:
        return
    for category in cat.subcats:
        compute_especificity(cat.subcats[category])

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

def get_matches(host, query):
    try:
        query_history[host+'_'+'+'.join(query)]
    except:

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
        query_history[host+'_'+'+'.join(query)] = int(total)
    return query_history[host+'_'+'+'.join(query)]

def compute_ecoverage(cat):
    d_size = 0
    for query in cat.queries:
        cat.matches += get_matches(host, query)
    d_size += cat.matches
    for category in cat.subcats:
        d_size += compute_ecoverage(cat.subcats[category])
    return d_size

def classify(cat):
    results = []
    if len(cat.subcats) == 0:
        return [cat]
    for c in cat.subcats:
        if cat.subcats[c].especi >= t_es and cat.subcats[c].matches >= t_ec:
            results.extend(classify(cat.subcats[c]))
    if len(results) == 0:
        return [cat]
    return results

def print_class(c):
    path = []
    current = c
    while current != None:
        path.append(current.name)
        current = current.parent
    path.reverse()
    print '/'.join(path)

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
        #sys.exit()

    t_es = 0.8
    t_ec = 100
    host = 'fifa.com'

    query_history = {}
    query_history = pickle.load(open(host+'-test.p','rb'))

    root = Category('Root', None)
    parse_file(root, 'root.txt')
    for cat in root.subcats:
        parse_file(root.subcats[cat], cat + '.txt')

    print "Classifying..."
    root.matches = compute_ecoverage(root)
    compute_especificity(root)


    pickle.dump(query_history, open(host+'-test.p','wb'))

    print
    print
    print
    print 'Classification:'
    classes = classify(root)
    for c in classes:
        print_class(c)

    print
    print
    print