import numpy


def rotate(p, origin=(0, 0), degrees=0):
    angle = numpy.deg2rad(degrees)
    R = numpy.array([[numpy.cos(angle), -numpy.sin(angle)],
                  [numpy.sin(angle),  numpy.cos(angle)]])
    # o = numpy.atleast_2d(origin)
    m = numpy.dot(R, p)
    return float(m.T[0]), float(m.T[1])
