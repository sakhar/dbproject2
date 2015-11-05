import operator
from string import ascii_letters
from subprocess import check_output
import time


def sampling(cat, query_history, host):
    """
    For a given category, and its associated queries,
    create the content summary.

    Inputs:
    - cat  : category object
    - query_history : history of already made queries
    - host : website to classify
    """
    output = open(cat.name+'-'+host+'.txt', 'w')
    words = {}
    matches = {}
    print 'Creating Content Summary for:', cat.name
    l = len(cat.associated)
    i = 1

    visited = []
    for query in set(cat.associated):
        print str(i)+'/'+str(l)
        i += 1
        docs = query_history[query][1]
        try:
            matches[query]
        except:
            matches[query] = 0
        matches[query] += query_history[query][0]
        print 'query:', query
        print 'matches:', matches[query]
        try:
            words[query]
        except:
            words[query] = 0
        time.sleep(1)
        for doc in docs:
            print
            if doc in visited:
                continue
            visited.append(doc)
            print
            print 'Getting page:', docs[doc].url
            print
            try:
                words_doc = process_url(docs[doc].url)
            except:
                continue
            for word in words_doc:
                try:
                    words[word]
                except:
                    words[word] = 0
                words[word] += 1
    sorted_list = sorted(words.items(), key=operator.itemgetter(0), reverse=False)
    for word in sorted_list:
        line = word[0]+'#'+str(float(word[1]))+'#'+str(matches.get(word[0],-1.0))+'\n'
        output.write(line)
        #print(line)
    output.close()


def process_url(url):
    """
    Transform the url content into text, removes brackets,
    non-english characters, replace by lowercases and
    remove the unnecessary whitespaces.

    Returns a set of tokens
    """
    content = check_output(['/usr/bin/lynx', '-dump', url])
    index_reference = content.find('\nReferences\n')

    if index_reference > -1:
        content = content[:index_reference]

    # get to lower case
    content = content.lower()
    list_content = list(content)
    output = []
    recording = True
    wrotespace = False

    for i in range(len(list_content)):
        if recording:
            if list_content[i] == '[':
                recording = False
                if not wrotespace:
                    output.append(' ')
                    wrotespace = True
                continue
            else:
                if list_content[i] in ascii_letters and ord(list_content[i]) < 128:
                    output.append(list_content[i])
                    wrotespace = False
                else:
                    if not wrotespace:
                        output.append(' ')
                        wrotespace = True
        else:
            if list_content[i] == ']':
                recording = True
                continue
    content = ''.join(output)
    list_content = content.split()
    return(set(list_content))


def get_path(cat):
    """
    Go up the category path and returns
    all encountered categories until
    the root is reached

    Example: Root/Computers/Programming
             -> [Programming, Computers, Root]
    """
    path = []
    current = cat
    if len(current.subcats) == 0:
        current = current.parent
    while current != None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path


def run(root, t_es, t_ec, query_history, classes, host):
    print 'Extracting topic content summaries...'
    for cat in classes:
        path = get_path(cat)
        for c in path:
            sampling(c, query_history, host)
