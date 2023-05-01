import numpy


def rotate(point, origin=(0, 0), degrees=0):
    angle = numpy.deg2rad(degrees)
    
    point = numpy.array(point)
    origin = numpy.array(origin)
    
    shape = point.shape
    
    if len(shape) > 1 and shape[1] >= 2:
        return numpy.array([rotate(p, degrees = degrees, origin = origin) for p in point])

    adjusted = (point - origin)
    
    cos_sin = numpy.array([numpy.cos(angle),numpy.sin(angle)])
    
    result = adjusted + cos_sin * adjusted[0] + numpy.flip(cos_sin) * adjusted[1]

    return result
