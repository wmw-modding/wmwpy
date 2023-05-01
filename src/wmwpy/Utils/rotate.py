import numpy


def rotate(point, degrees=0, origin=(0, 0)):
    angle = numpy.deg2rad(degrees)
    
    point = numpy.array(point)
    # origin = numpy.array(origin)
    
    shape = point.shape
    
    if len(shape) > 1 and shape[1] >= 2:
        return numpy.array([rotate(p, degrees = degrees, origin = origin) for p in point])
    
    R = numpy.array([[numpy.cos(angle), -numpy.sin(angle)],
                  [numpy.sin(angle),  numpy.cos(angle)]])
    # o = numpy.atleast_2d(origin)
    m = numpy.dot(R, point)
    return float(m.T[0]), float(m.T[1])
