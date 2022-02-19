import math
from turtle import pen
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

def getSampledPoints(path, samples=1000, offset=(0,0), degrees=0):
    svgdoc = minidom.parse(path)
    svgpathdarr = [element.getAttribute('d') for element in svgdoc.getElementsByTagName('path')]
    svgdoc.unlink()
    svgpathd = str(svgpathdarr[-1])
    bezierpath = svg.path.parse_path(svgpathd)
    points = [Point(x=p.real+offset[0], y=p.imag+offset[1]) for p in (bezierpath.point(i/samples) for i in range(samples+1))]
    size = getSvgDimesions(points)
    return points, size

def exportSvgPoints(points, path):
    builder = SVGBuilder()
    builder.GlobalStyle.penWidth = 0
    fillColour = 0x60138013
    strokeColour = 0xFF003300
    builder.AddPolygon(points, fillColour, strokeColour)
    builder.SaveToFile('./output.svg')

def getUnion(objectA, objectB, offset=(0,0)):
    objectB = offsetPoints(objectB, offset)
    subj, clip = [], []
    subj.append(objectA)
    clip.append(objectB)
    c = Clipper()
    c.AddPolygons(subj, PolyType.Subject)
    c.AddPolygons(clip, PolyType.Clip)
    solution = []
    c.Execute(ClipType.Union, solution)
    return solution

def offsetPoints(points, offset=(0,0)):
    output = []
    for point in points:
        ox, oy = point.x + offset[0], point.y + offset[1]
        output.append(Point(x=ox, y=oy))
    return output

# def combinePoints():

GEAR_POINTS, GEAR_SIZE = getSampledPoints(path='gear.svg')

union = getUnion(GEAR_POINTS, GEAR_POINTS, (0, 0))

exportSvgPoints(union, '')