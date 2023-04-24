from lxml import etree

def findTag(root : etree.ElementBase, tag : str) -> etree.Element:
    element = 0
    curTag = ''
    for e in root:
        print(e.tag)
        if e.tag is etree.Comment:
            continue
        curTag = e.tag
        if curTag == tag:
            return e
        
    return None

def strbool(value : str) -> bool:
    if isinstance(value, bool):
        return value
    else:
        return value.lower() in ("yes", "true", "t", "1")
