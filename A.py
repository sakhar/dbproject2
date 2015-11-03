import pickle
import urllib2
import xml.etree.ElementTree as ET
from main import Category
from main import headers
from main import Document

query_history = {}
def compute_especificity(cat, t_es, t_ec):
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
        compute_especificity(cat.subcats[category], t_es, t_ec)

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
    docs = {}
    try:
        query_history['+'.join(query)]
    except:

        url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=' \
              '%27site%3a' \
              +host+\
              '%20' \
              +'+'.join(query)+\
              '%27&$top=4&$format=Atom'
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        xml_root = ET.parse(response)
        entry = xml_root.find('{http://www.w3.org/2005/Atom}entry')
        content = entry.find('{http://www.w3.org/2005/Atom}content')
        properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
        total = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}WebTotal').text
        query_history[host+'_'+'+'.join(query)] = int(total)

        link = entry.find('{http://www.w3.org/2005/Atom}link')
        inline = link.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}inline')
        feed = inline.find('{http://www.w3.org/2005/Atom}feed')
        entries = feed.findall('{http://www.w3.org/2005/Atom}entry')
        print 'query:', query
        print 'len:', len(entries)
        for entry in entries:
            content = entry.find('{http://www.w3.org/2005/Atom}content')
            properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
            ID = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}ID').text
            Title = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}Title').text
            Description = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}Description').text
            DisplayUrl = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}DisplayUrl').text
            Url = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}Url').text
            doc = Document(ID, Title, Description, DisplayUrl, Url)
            docs[Url] = doc

        query_history['+'.join(query)] = (int(total), docs)
    return query_history['+'.join(query)][0], query_history['+'.join(query)][1]

def compute_ecoverage(host, cat):
    d_size = 0
    doc = {}
    for query in cat.queries:
        #cat.matches += get_matches(host, query)
        matches, docs = get_matches(host, query)
        cat.matches = matches
    d_size += cat.matches
    for category in cat.subcats:
        d_size += compute_ecoverage(host, cat.subcats[category])
    return d_size

def classify(cat, t_es, t_ec):
    results = []
    if len(cat.subcats) == 0:
        return [cat]
    for c in cat.subcats:
        for query in cat.subcats[c].queries:
            cat.docs.update(query_history['+'.join(query)][1])
        if cat.subcats[c].especi >= t_es and cat.subcats[c].matches >= t_ec:
            results.extend(classify(cat.subcats[c], t_es, t_ec))
            cat.docs.update(cat.subcats[c].docs)
    if len(results) == 0:
        return [cat]
    return results

def print_class(c):
    '''
    :param c: object of type Category
    :return: nothin
    print the category c full path (example: Root/Computers/Programming)
    '''
    path = []
    current = c
    while current != None:
        path.append(current.name)
        current = current.parent
    path.reverse()
    print '/'.join(path)

def run(host, t_es, t_ec):

    global query_history
    try:
        query_history = pickle.load(open(host+'-test.p','rb'))
    except:
        query_history = {}

    # part 1
    root = Category('Root', None)
    parse_file(root, 'root.txt')
    for cat in root.subcats:
        parse_file(root.subcats[cat], cat + '.txt')

    print "Classifying..."
    root.matches = compute_ecoverage(host, root)
    compute_especificity(root, t_es, t_ec)

    pickle.dump(query_history, open(host+'-test.p','wb'))

    print
    print
    print
    print 'Classification:'
    classes = classify(root, t_es, t_ec)

    # print each category full path (example: Root/Computers/Programming)
    for c in classes:
        print_class(c)

    print
    print
    print
    l = 0
    i = 0
    for c in root.subcats:
        for query in root.subcats[c].queries:
                print i,'/',l
                print query_history['+'.join(query)][1]
                i += 1
    return root