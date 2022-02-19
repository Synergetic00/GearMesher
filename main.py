import math
import svgutils
from clipper import Point
from xml.dom import minidom
from svg.path import parse_path
from wrapper import Clipper, PolyFillType, PolyType, ClipType, SVGBuilder

def rotateSvgFile(pathSVG, degrees, middle):
    svg = svgutils.transform.fromfile(pathSVG)
    originalSVG = svgutils.compose.SVG(pathSVG)
    originalSVG = originalSVG.rotate(degrees, x=middle[0], y=middle[1])
    figure = svgutils.compose.Figure(svg.height, svg.width, originalSVG)
    figure.save('temp.svg')

def convertToPointArray(tupleArray, xoff=0, yoff=0):
    output = []
    for tup in tupleArray:
        pt = Point(x=tup[0] + xoff, y=tup[1] + yoff)
        output.append(pt)
    return output

def getSampledSvgPoints(pathSVG, samples=2000):
    doc = minidom.parse(pathSVG)
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    doc.unlink()
    svg_path = path_strings[-1]
    bezier_path = parse_path(svg_path)
    num_of_samples = samples
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

def subFromSVG(radii, angle):
    subj, clip = [], []
    cpoints, _ = getSampledSvgPoints('gear.svg')
    rotateSvgFile('gear.svg', angle, cpoints[4])
    _, clipSVG = getSampledSvgPoints('gear.svg')
    _, subjSVG = getSampledSvgPoints('output.svg')
    subjArr = convertToPointArray(subjSVG, 0, 0)
    dxoff = -int(cpoints[2]) - cpoints[4][1]
    dyoff = -int(cpoints[0]) - cpoints[4][0]
    cxoff = dxoff + (radii * math.cos(math.radians(angle)))
    cyoff = dyoff + (radii * math.sin(math.radians(angle)))
    clipArr = convertToPointArray(clipSVG, cxoff, cyoff)
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
    svgBuilder.SaveToFile('./output.svg', invScale, 0)

def performSetup(pathSVG, radii):
    svg = svgutils.transform.fromfile(pathSVG)
    originalSVG = svgutils.compose.SVG(pathSVG)
    size, _ = getSampledSvgPoints('circle.svg')
    scalew = radii / size[3]
    scaleh = radii / size[1]
    originalSVG = originalSVG.scale(x=scalew, y=scaleh)
    figure = svgutils.compose.Figure(svg.height, svg.width, originalSVG)
    figure.save('output.svg')

RADIUS = 224
performSetup('circle.svg', RADIUS)
TEETH = 16
for i in range(0, TEETH+1, 1):
    rot = (90.0/TEETH) * i
    subFromSVG(RADIUS, rot)