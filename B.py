def samping(cat, query_history):
    words = {}
    print 'Creating Content Summary for:', cat.name
    l = len(cat.associated)
    i = 1
    for query in cat.associated:
        print str(i)+'/'+str(l)
        i+=1
        docs = query_history[query][1]
        for doc in docs:
            print
            print 'Getting page:', docs[doc].url
            print
            words_doc = process_url(docs[doc].url)
            for word in words_doc:
                try:
                    words[word]
                except:
                    words[word] = 0
                words[word] += 1
def process_url(url):
    '''TODO'''
    pass

def get_path(cat):
    path = []
    current = cat.parent
    while current != None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path

def run(root, t_es, t_ec, query_history, classes):
    '''
    for c in classes:
        print c.name, len(root.associated)
    print len(root.associated)
    for cat in root.subcats:
        print root.subcats[cat].name, len(root.subcats[cat].docs)
    print 'root', len(root.docs)

    print
    print
    '''
    print 'Extracting topic content summaries...'
    for cat in classes:
        path = get_path(cat)
        for c in path:
            samping(c, query_history)


