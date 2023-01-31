from lxml import etree

def findTag(root, tag):
    element = 0
    curTag = ''
    for e in root:
        print(e.tag)
        if isinstance(e, etree.Comment):
            continue
        curTag = e.tag
        if curTag == tag:
            return e
            break
