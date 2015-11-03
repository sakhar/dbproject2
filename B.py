def samping(cat, t_es, t_ec):
    results = []
    if len(cat.subcats) == 0:
        return [cat.docs]
    for c in cat.subcats:
        if cat.subcats[c].especi >= t_es and cat.subcats[c].matches >= t_ec:
            results.extend(samping(cat.subcats[c], t_es, t_ec))
            if cat.parent != None:
                cat.parent.docs.update(cat.subcats[c].docs)
    if len(results) == 0:
        return [cat]
    return results
def run(root, t_es, t_ec):

    for cat in root.subcats:
        print root.subcats[cat].name, len(root.subcats[cat].docs)
    print 'root', len(root.docs)

    print
    print


