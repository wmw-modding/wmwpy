import numpy


def rotate(point : tuple[float, float], degrees : float = 0):
    """Rotate a point around (0,0)

    Args:
        point (tuple[float,float]): Point to rotate.
        degrees (float, optional): Amount of degrees to rotate. Defaults to 0.

    Returns:
        tuple[float,float]: New point (x,y)
    """
    angle = numpy.deg2rad(degrees)
    
    point = numpy.array(point)
    # origin = numpy.array(origin)
    
    shape = point.shape
    
    if len(shape) > 1 and shape[1] >= 2:
        return numpy.array([rotate(p, degrees = degrees) for p in point])
    
    R = numpy.array([[numpy.cos(angle), -numpy.sin(angle)],
                  [numpy.sin(angle),  numpy.cos(angle)]])
    # o = numpy.atleast_2d(origin)
    m = numpy.dot(R, point)
    return float(m.T[0]), float(m.T[1])
