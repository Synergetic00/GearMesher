from xml.dom import minidom
from svg.path import parse_path

doc = minidom.parse('circle.svg')  # parseString also exists
path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
doc.unlink()
svg_path = path_strings[-1]
bezier_path = parse_path(svg_path)
num_of_samples = 10
pts = [ (p.real,p.imag) for p in (bezier_path.point(i/num_of_samples) for i in range(0, num_of_samples+1))]
print(pts)