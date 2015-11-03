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
        self.docs = {}
        self.matches = 0
        self.parent = parent
        self.especi = 0


# Class Document to store each document information
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
        print 'example: python main.py 0.6 100 health.com'
        #sys.exit()

    t_es = 0.8
    t_ec = 100
    host = 'fifa.com'

    print 'Part A:'
    print
    root = A.run(host, t_es, t_ec)
    print
    print 'Part B:'
    print
    B.run(root, t_es, t_ec)