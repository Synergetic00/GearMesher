import math
from turtle import pen
import svg.path
import svgutils
from xml.dom import minidom
from clipper import Point, Clipper, PolyFillType, PolyType, ClipType, SVGBuilder

def getSvgDimesions(points):
    xpoints, ypoints = zip(*points)
    upper = min(ypoints)
    lower = max(ypoints)
    left = min(xpoints)
    right = max(xpoints)
    middle = ((right-left)/2.0, (lower-upper)/2.0)
    return (upper, lower, left, right, middle)

def getRotatedArr(points, middle, degrees):
    output = []
    p, q = middle
    theta = math.radians(degrees)
    for point in points:
        x, y = point.x , point.y
        xp = (x - p) * math.cos(theta) - (y - q) * math.sin(theta) + p
        yp = (x - p) * math.sin(theta) + (y - q) * math.cos(theta) + q
        output.append(Point(x=xp, y=yp))
    return output

def getSampledPoints(path, samples=1000, offset=(0,0), middle=(0,0), degrees=0):
    svgdoc = minidom.parse(path)
    svgpathdarr = [element.getAttribute('d') for element in svgdoc.getElementsByTagName('path')]
    svgdoc.unlink()
    svgpathd = str(svgpathdarr[-1])
    bezierpath = svg.path.parse_path(svgpathd)
    points = [Point(x=p.real+offset[0], y=p.imag+offset[1]) for p in (bezierpath.point(i/samples) for i in range(samples+1))]
    rotatedPoints = getRotatedArr(points, middle, degrees)
    size = getSvgDimesions(points)
    return rotatedPoints, size

def exportSvgPoints(points, path):
    svgBuilder = SVGBuilder()
    svgBuilder.GlobalStyle.penWidth = 0
    svgBuilder.AddPolygons(points, 0x60138013, 0xFF003300)
    svgBuilder.SaveToFile('./' + path, 1, 0)

def offsetPoints(points, offset=(0,0)):
    output = []
    for point in points:
        ox, oy = point.x + offset[0], point.y + offset[1]
        output.append(Point(x=ox, y=oy))
    return output

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

def getResampledArr(original, samples=1500):
    length = len(original)
    ratio = samples / length
    if ratio >= 1.0: return original
    resampled = []
    counter = 0.0
    for i in range(length):
        if counter > 1.0:
            resampled.append(original[i])
            counter = 0.0
        counter += ratio
    return resampled

GEAR_POINTS, GEAR_SIZE = getSampledPoints(path='resources/gear.svg', degrees=0)
union = getUnion(GEAR_POINTS, GEAR_POINTS)

RADIUS = 300
NUM = 10

for i in range(NUM):
    degrees = (90/NUM) * i
    rotatedGear, rotatedSize = getSampledPoints(path='resources/gear.svg', middle=GEAR_SIZE[4], degrees=degrees)
    dxoff = int(GEAR_SIZE[2]) - GEAR_SIZE[4][1]
    dyoff = int(GEAR_SIZE[0]) - GEAR_SIZE[4][0]
    cxoff = (RADIUS * math.cos(math.radians(degrees)))
    cyoff = (RADIUS * math.sin(math.radians(degrees)))
    resampled = getResampledArr(union[0], samples=1500)
    union = getUnion(resampled, rotatedGear, (cxoff, cyoff))

exportSvgPoints(union, 'resources/output.svg')