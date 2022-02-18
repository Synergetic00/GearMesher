# from PIL import Image
# from tkinter import filedialog
import numpy as np
# from potrace import Bitmap
import pyclipper
import clipper_demo as cd

gearRatio = 2
gearOverlap = 1.0
computationSteps = 20

# inputImage = Image.open('gear.png').convert(mode='L')
# npDataArr = np.asarray(inputImage)
# ptBitmap = Bitmap(npDataArr)
# ptPath = ptBitmap.trace()

# print(ptPath.curves)

from xml.dom import minidom
from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, parse_path
from tkinter import Tk, Canvas, Frame, BOTH

doc = minidom.parse('circle2.svg')  # parseString also exists
path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
doc.unlink()
svg_path = path_strings[-1]
bezier_path = parse_path(svg_path)

# NUM_SAMPLES = 10

# myPath = []
# for i in range(NUM_SAMPLES):
#     myPath.append(bezier_path.point(i/(NUM_SAMPLES-1)))

# print(myPath)

num_of_samples = 100  # number of line segments to draw

# pts = []
# for i in range(0,n+1):
#     f = i/n  # will go from 0.0 to 1.0
#     complex_point = path.point(f)  # point(x) is method on svg.path to return point x * 100  percent along path
#     pts.append((complex_point.real, complex_point.imag))

pts = [ (p.real,p.imag) for p in (bezier_path.point(i/num_of_samples) for i in range(0, num_of_samples+1))]  # list comprehension version or loop above

print(pts)

class SVGcurve(Frame):

    def __init__(self, pts):
        super().__init__()
        self.pts = pts
        self.initUI()

    def initUI(self):
        self.master.title("svg")
        self.pack(fill=BOTH, expand=1)

        canvas = Canvas(self)
        x0, y0 = self.pts[0]
        for x1, y1 in self.pts[1:]:
            canvas.create_line(x0/5, y0/5, x1/5, y1/5)
            x0, y0 = x1/5, y1/5

        canvas.pack(fill=BOTH, expand=1)


root = Tk()
ex = SVGcurve(pts)  # convert i_pts to (x,y) tuple list
root.geometry("400x600+300+300")
root.mainloop()

# from svgpathtools import svg2paths
# paths, attributes = svg2paths('gear.svg')
# print(paths)

# print(len(paths))