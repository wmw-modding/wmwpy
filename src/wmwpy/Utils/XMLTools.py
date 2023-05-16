from lxml import etree

def findTag(root : etree.ElementBase, tag : str) -> etree.ElementBase:
    """Find an element in an etree element.

    Args:
        root (etree.ElementBase): The root element to search.
        tag (str): The element to find.

    Returns:
        etree.ElementBase: etree Element
    """
    element = 0
    curTag = ''
    for e in root:
        # print(e.tag)
        if e.tag is etree.Comment:
            continue
        curTag = e.tag
        if curTag == tag:
            return e
        
    return None

def strbool(value : str) -> bool:
    """Convert a string to a bool

    Args:
        value (str): String. Can be 'true', 'false', 't', 'f', '0', or '1'. The string is case insensative.

    Returns:
        bool: Python `bool` object.
    """
    if isinstance(value, bool):
        return value
    else:
        return value.lower() in ("yes", "true", "t", "1")
