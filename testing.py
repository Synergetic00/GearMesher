import math
import svg.path
import svgutils
from clipper import Point
from xml.dom import minidom
from wrapper import Clipper, PolyFillType, PolyType, ClipType, SVGBuilder

def getSvgDimesions(points):
    xpoints, ypoints = zip(*points)
    upper = min(ypoints)
    lower = max(ypoints)
    left = min(xpoints)
    right = max(xpoints)
    middle = ((right-left)/2.0, (lower-upper)/2.0)
    return (upper, lower, left, right, middle)

def getSampledPoints(path, samples=1000):
    svgdoc = minidom.parse(path)
    svgpathdarr = [element.getAttribute('d') for element in svgdoc.getElementsByTagName('path')]
    svgdoc.unlink()
    svgpathd = str(svgpathdarr[-1])
    bezierpath = svg.path.parse_path(svgpathd)
    points = [Point(x=p.real, y=p.imag) for p in (bezierpath.point(i/samples) for i in range(samples+1))]
    size = getSvgDimesions(points)
    return points, size

# def combinePoints():

GEAR_POINTS, GEAR_SIZE = getSampledPoints('gear.svg')

