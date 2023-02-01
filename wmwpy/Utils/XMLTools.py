from lxml import etree

def findTag(root : etree.Element, tag : str) -> etree.Element:
    element = 0
    curTag = ''
    for e in root:
        print(e.tag)
        if e.tag is etree.Comment:
            continue
        curTag = e.tag
        if curTag == tag:
            return e
            break
