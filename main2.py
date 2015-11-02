import base64
import urllib2
import xml.etree.ElementTree as ET
import pickle

# load the cache of past queries
g = open('query_history.p', 'rb')
query_history = pickle.load(g)
g.close()

# define the tree of labels
class Node(object):

    def __init__(self, name='', children=[], probes=None):

        self.name = name
        self.children = children
        self.probes = probes

    def make_probes(self, filename):
        "From a file of probes, get the probes of the children of one node"

        for child in self.children:
            child.probes = []

        f = open(filename, 'r')
        for line in f.read().splitlines():
            query = line.rsplit()
            for child in self.children:
                if query[0] == child.name:
                    child.probes.append('+'.join(query[1:]))

# create the tree, with the probes
def make_tree():

    root = Node('Root')
    root.children = [Node('Computers'), Node('Health'), Node('Sports')]
    root.children[0].children = [Node('Hardware'), Node('Programming')]
    root.children[1].children = [Node('Fitness'), Node('Diseases')]
    root.children[2].children = [Node('Basketball'), Node('Soccer')]

    root.make_probes('root.txt')
    root.children[0].make_probes('computers.txt')
    root.children[1].make_probes('health.txt')
    root.children[2].make_probes('sports.txt')
    return root

# requests the number of result
def nb_query(site, query):
    try:
        query_history[site+' '+query]
    except KeyError:
        bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + site + '%20' + query + '%27&$top=10&$format=Atom'
        accountKey = 'TZUv0QfVBhxRvxnx7mruxxYhy/yR5uLoKq5PKJrNUBs'
        accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
        headers = {'Authorization': 'Basic ' + accountKeyEnc}
        req = urllib2.Request(bingUrl, headers=headers)
        response = urllib2.urlopen(req)
        tree = ET.parse(response)

        root = tree.getroot()
        entry = root.find('{http://www.w3.org/2005/Atom}entry')
        content = entry.find('{http://www.w3.org/2005/Atom}content')
        properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
        web_total = int(properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}WebTotal').text)

        query_history[site+' '+query] = web_total

    return query_history[site+' '+query]


def classify(site, node, t_es, t_ec, nb_total=-1, result = []):
    # compute the total number of results for the given site
    if nb_total < 0:
        nb_total = nb_query(site, '')

    # case where we are on a leaf tree
    if node.children == []:
        return node.name

    # compute coverage specificity for
    # all children of the current node
    # in a depth first search method
    for child in node.children:
        n_ec = 0
        for query in child.probes:
            n_ec += 1
            n_ec += nb_query(site, query)
        if n_ec > t_ec and n_ec > t_es*nb_total:
            result.append(child.name)
            classify(site, child, t_es, t_ec, nb_total, result)
    return result

root = make_tree()
print(classify('diabetes.org', root, .6, 100))

f = open('query_history.p', 'wb')
pickle.dump(query_history, f)
f.close()