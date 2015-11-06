'''
Columbia University
COMS E6111 Advanced Database Systems, Fall 2015
Project 2

Students:
Robert Dadashi-Tazehozi, UNI: rd2669
Sakhar Alkhereyf       , UNI: sa3147

'''

import base64
import sys
import A
import B

accountKey = 'XfbHf/vIn9YQOGFXSYwPnxOOmIWdeM95n39nD5s4FxI'
accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}


class Category:
    '''
    Class Category
    name:       name of the category (e.g. Root)
    subcats:    dictionary of Category objects to store sub-categories
                key: category name, value: object of type Category

    '''
    def __init__(self, name, parent):
        self.name = name
        self.queries = []
        self.subcats = {}
        self.matches = 0
        self.parent = parent
        self.especi = 0
        self.associated = []


# Class Document to store each returned website information
class Document():
    def __init__(self, id, title, des, disp, url):
        self.id = id
        self.title = title
        self.des = des
        self.disp = disp
        self.url = url


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
        print '<t_es> should be a real number between 0-1 and <t_ec> an integer > 1'
        print 'example: python main.py 0.6 100 health.com'
        sys.exit()

    print 'Part A:\n'
    root, query_history, classes = A.run(host, t_es, t_ec)

    print '\nPart B:\n'
    B.run(query_history, classes, host)
