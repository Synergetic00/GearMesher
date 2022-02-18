from clipper import *
from wrapper import *
import os
from xml.dom import minidom
from svg.path import parse_path
import svgutils

# def getRotatedSVG(pathSVG, degrees=0):
#     svg = svgutils.transform.fromfile(pathSVG)
#     originalSVG = svgutils.compose.SVG(pathSVG)
#     originalSVG = originalSVG.rotate(degrees, x=324.5998, y=317.5917)
#     # originalSVG.move(svg.height, 10)
#     figure = svgutils.compose.Figure(svg.height, svg.width, originalSVG)
#     figure.save('temp.svg')

def getPointArrayTempo(tupleArray, xoff=0, yoff=0):
    output = []
    for tup in tupleArray:
        pt = Point(x=tup[0] + xoff, y=tup[1] + yoff)
        output.append(pt)
    return output

def loadSVGShit(pathSVG, rot=0):
    doc = minidom.parse(pathSVG)
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    doc.unlink()
    svg_path = path_strings[-1]
    bezier_path = parse_path(svg_path)
    num_of_samples = 2000
    pts = [ (p.real,p.imag) for p in (bezier_path.point(i/num_of_samples) for i in range(0, num_of_samples+1))]
    upper, left, right, lower = pts[0][1], pts[0][0], 0, 0
    for point in pts:
        if point[0] < left:
            left = point[0]
        if point[1] < upper:
            upper = point[1]
        if point[0] > right:
            right = point[0]
        if point[1] > lower:
            lower = point[1]
    middle = (int((right-left)/2), int((lower-upper)/2))
    return (upper, lower, left, right, middle), pts


# subjSVG = loadSVGShit('circle.svg', 40)
# clipSVG = loadSVGShit('gear.svg', 40)
# subjArr = getPointArrayTempo(subjSVG, 0, 0)
# clipArr = getPointArrayTempo(clipSVG, 0, 0)


################
# Boiler Plate #
################

# clipSVG = loadSVGShit('gear.svg')

def subFromSVG(diam, angle):
    subj, clip = [], []
    cpoints, clipSVG = loadSVGShit('gear.svg')
    _, subjSVG = loadSVGShit('circle.svg')
    subjArr = getPointArrayTempo(subjSVG, 0, 0)
    dxoff = -int(cpoints[2]) - cpoints[4][1]
    dyoff = -int(cpoints[0]) - cpoints[4][0]
    cxoff = dxoff + ((diam/2.) * math.cos(math.radians(angle)))
    cyoff = dyoff + ((diam/2.) * math.sin(math.radians(angle)))
    clipArr = getPointArrayTempo(clipSVG, cxoff, cyoff)
    subj.append(subjArr)
    clip.append(clipArr)
    c = Clipper()
    solution = []
    pft = PolyFillType.EvenOdd
    scaleExp = 0
    scale = math.pow(10, scaleExp)
    invScale = 1.0 / scale
    c.AddPolygons(subj, PolyType.Subject)
    c.AddPolygons(clip, PolyType.Clip)
    c.Execute(ClipType.Difference, solution, pft, pft)
    svgBuilder = SVGBuilder()
    svgBuilder.GlobalStyle.fillType = pft
    svgBuilder.GlobalStyle.penWidth = 0
    svgBuilder.AddPolygons(solution, 0x60138013, 0xFF003300)
    svgBuilder.SaveToFile('./output.svg', invScale, 100)

# for i in range(0, 628, 10):
#     x_offset = ((800/2.) * math.cos(i/100))
#     y_offset = ((800/2.) * math.sin(i/100))
subFromSVG(1000, 45)