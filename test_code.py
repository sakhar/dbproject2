__author__ = 'sakhar'
import urllib2
import base64
import sys
import xml.etree.ElementTree as ET
# Just to test code (will not be submitted)
import pickle

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
            print cat.subcats[c].name
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

if __name__ == '__main__':
    t_es = 0.8
    t_ec = 100
    #host = 'fifa.com'
    host = 'fifa.com'
    '''
    root = Category('Root', None)
    parse_file(root,'root.txt')
    for cat in root.subcats:
        parse_file(root.subcats[cat],cat+'.txt')
    pickle.dump(root, open(host+'-test.p','wb'))
    '''
    #
    root = pickle.load(open(host+'-test.p','rb'))
    print "Classifying..."
    root.matches = compute_ecoverage(root)
    compute_especificity(root)
    classes = classify(root)
    for c in classes:
        print_class(c)

