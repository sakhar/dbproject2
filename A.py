'''
Columbia University
COMS E6111 Advanced Database Systems, Fall 2015
Project 2

Students:
Robert Dadashi-Tazehozi, UNI: rd2669
Sakhar Alkhereyf       , UNI: sa3147

'''

import pickle
import urllib2
import xml.etree.ElementTree as ET
from main import Category
from main import headers
from main import Document

# create a cache to save previous queries
query_history = {}


def compute_ecoverage(host, cat):
    """
    Compute the ESpecificity of the labels
    in a recursive way

    Inputs:
    - host : website where we adress the query
    - cat  : Category object
    """
    d_size = 0
    for query in cat.queries:
        matches, docs = get_matches(host, query)
        cat.matches += matches
    d_size += cat.matches
    for category in cat.subcats:
        d_size += compute_ecoverage(host, cat.subcats[category])
    return d_size


def compute_especificity(cat, t_es, t_ec):
    """
    Compute the ESpecificity of the labels
    in a recursive way

    Inputs:
    - cat  : Category object
    - t_es : threshold for ESpecificity
    - t_ec : threshold for ECoverage

    """
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
    """
    Go through on the file with the list of queries
    for one category and add each query to the right
    subcategory

    Input:
    - cat  : Category object
    - file : name of the file containing the queries
    """
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
    """
    For a host and a query, get the number of results and
    the top 4 matching results and update the cache accordingly

    Inputs:
    - host  : host website where to adress the queries
    - query : a list of words representing the query
    """
    docs = {}
    try:
        query_history[' '.join(query)]
    except:

        url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a'\
              + host + '%20' + '+'.join(query) + '%27&$top=4&$format=Atom'
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        xml_root = ET.parse(response)
        entry = xml_root.find('{http://www.w3.org/2005/Atom}entry')
        content = entry.find('{http://www.w3.org/2005/Atom}content')
        properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
        total = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}WebTotal').text

        link = entry.find('{http://www.w3.org/2005/Atom}link')
        inline = link.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}inline')
        feed = inline.find('{http://www.w3.org/2005/Atom}feed')
        entries = feed.findall('{http://www.w3.org/2005/Atom}entry')

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

        query_history[' '.join(query)] = (int(total), docs)
    return query_history[' '.join(query)][0], query_history[' '.join(query)][1]


def classify(cat, t_es, t_ec):
    """
    Implementation of the algorithm suggested in the figure 4
    'Classification-Aware Hidden-Web Text Database Selection'
    (2008) by Ipeirotis and Gravano

    Classifies a host into a set of category

    Inputs:
    - cat  : Category object
    - t_es : threshold for ESpecificity
    - t_ec : threshold for ECoverage
    """
    results = []
    if len(cat.subcats) == 0:
        return [cat]
    for c in cat.subcats:
        for query in cat.subcats[c].queries:
            cat.associated.append(' '.join(query))
        if cat.subcats[c].especi >= t_es and cat.subcats[c].matches >= t_ec:
            results.extend(classify(cat.subcats[c], t_es, t_ec))
            cat.associated.extend(cat.subcats[c].associated)
    if len(results) == 0:
        return [cat]
    return results


def print_class(c):
    """
    Print the category c full path
    Example: Programming -> Root/Computers/Programming

    Inputs:
    - cat  : Category object
    """
    path = []
    current = c
    while current is not None:
        path.append(current.name)
        current = current.parent
    path.reverse()
    print '/'.join(path)


def run(host, t_es, t_ec):
    """
    Assign the queries and compute ECoverage and
    ESpecificity and classifies the host accordingly
    to the thresholds

    Inputs:
    - host : host website url
    - t_es : threshold for ESpecificity
    - t_ec : threshold for ECoverage
    """
    # Load the queries history
    global query_history
    try:
        query_history = pickle.load(open(host+'-'+str(t_es)+'-'+str(t_ec)+'-history.p','rb'))
    except:
        query_history = {}
    # Assign the queries
    root = Category('Root', None)
    parse_file(root, 'root.txt')
    for cat in root.subcats:
        parse_file(root.subcats[cat], cat + '.txt')

    print "Classifying..."
    root.matches = compute_ecoverage(host, root)
    compute_especificity(root, t_es, t_ec)
    pickle.dump(query_history, open(host+'-'+str(t_es)+'-'+str(t_ec)+'-history.p','wb'))
    print '\n\n\nClassification:'
    classes = classify(root, t_es, t_ec)
    # Print each category full path (example: Root/Computers/Programming)
    for c in classes:
        print_class(c)
    return root, query_history, classes
