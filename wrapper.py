from clipper import *

def SaveToFile(filename, polys, scale = 1.0):
    invScale = 1.0 / scale
    try:
        f = open(filename, 'w')
        try:
            if invScale == 1:
                for poly in polys:
                    for pt in poly:
                        f.write("{0}, {1}\n".format(pt.x, pt.y))
                    f.write("\n")
            else:
                for poly in polys:
                    for pt in poly:
                        f.write("{0:.4f}, {1:.4f}\n".format(pt.x * invScale, pt.y * invScale))
                    f.write("\n")
        finally:
            f.close()
    except:
        return

class SVGBuilder(object):

    def HtmlColor(self, val):
        return "#{0:06x}".format(val & 0xFFFFFF)

    def AlphaClr(self, val):
        return "{0:.2f}".format(float(val >> 24)/255)

    class StyleInfo(object):
        def __init__(self):
            self.fillType = PolyFillType.EvenOdd
            self.brushClr = 0
            self.penClr = 0
            self.penWidth = 0.8
            self.showCoords = False

    class StyleInfoPlus(StyleInfo):

        def __init__(self):
            SVGBuilder.StyleInfo.__init__(self)
            self.polygons = []
            self.textlines = []

    def __init__(self):
        self.GlobalStyle = SVGBuilder.StyleInfo()
        self.PolyInfoList = []
        self.PathHeader = " <path d=\""
        self.PathFooter = "\"\n style=\"fill:{0}; fill-opacity:{1}; fill-rule:{2}; stroke:{3}; stroke-opacity:{4}; stroke-width:{5:.2f};\" filter=\"url(#Gamma)\"/>\n\n"
        self.Header = """<?xml version=\"1.0\" standalone=\"no\"?>
<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.0//EN\"
\"http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd\">
\n<svg width=\"{0}px\" height=\"{1}px\" viewBox=\"0 0 {0} {1}\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">
  <defs>
    <filter id="Gamma">
      <feComponentTransfer>
        <feFuncR type="gamma" amplitude="1" exponent="0.3" offset="0" />
        <feFuncG type="gamma" amplitude="1" exponent="0.3" offset="0" />
        <feFuncB type="gamma" amplitude="1" exponent="0.3" offset="0" />
      </feComponentTransfer>
    </filter>
  </defs>\n\n"""

    def AddPolygon(self, poly, brushColor, penColor):
        if poly is None or len(poly) == 0: return
        pi = self.StyleInfoPlus()
        pi.penWidth = self.GlobalStyle.penWidth
        pi.fillType = self.GlobalStyle.fillType
        pi.showCoords = self.GlobalStyle.showCoords
        pi.brushClr = brushColor
        pi.penClr = penColor
        pi.polygons.append(poly)
        self.PolyInfoList.append(pi)

    def AddPolygons(self, polys, brushColor, penColor):
        if polys is None or len(polys) == 0: return
        pi = self.StyleInfoPlus()
        pi.penWidth = self.GlobalStyle.penWidth
        pi.fillType = self.GlobalStyle.fillType
        pi.showCoords = self.GlobalStyle.showCoords
        pi.brushClr = brushColor
        pi.penClr = penColor
        pi.polygons = polys
        self.PolyInfoList.append(pi)

    def SaveToFile(self, filename, invScale = 1.0, margin = 10):
        if len(self.PolyInfoList) == 0: return False
        if invScale == 0: invScale = 1.0
        if margin < 0: margin = 0
        pi = self.PolyInfoList[0]
        # get bounding rect ...
        left = right = pi.polygons[0][0].x
        top = bottom = pi.polygons[0][0].y
        for pi in self.PolyInfoList:
            for p in pi.polygons:
                for ip in p:
                    if ip.x < left: left = ip.x
                    if ip.x > right: right = ip.x
                    if ip.y < top: top = ip.y
                    if ip.y > bottom: bottom = ip.y
        left *= invScale
        top *= invScale
        right *= invScale
        bottom *= invScale
        offsetX = -left + margin
        offsetY = -top + margin

        f = open(filename, 'w')
        m2 = margin * 2
        f.write(self.Header.format(right - left + m2, bottom - top + m2))
        for pi in self.PolyInfoList:
            f.write(self.PathHeader)
            for p in pi.polygons:
                cnt = len(p)
                if cnt < 3: continue
                f.write(" M {0:.2f} {1:.2f}".format(p[0].x * invScale + offsetX, p[0].y * invScale + offsetY))
                for i in range(1,cnt):
                    f.write(" L {0:.2f} {1:.2f}".format(p[i].x * invScale + offsetX, p[i].y * invScale + offsetY))
                f.write(" z")
            fillRule = "evenodd"
            if pi.fillType != PolyFillType.EvenOdd: fillRule = "nonzero"
            f.write(self.PathFooter.format(self.HtmlColor(pi.brushClr),
                self.AlphaClr(pi.brushClr), fillRule,
                self.HtmlColor(pi.penClr), self.AlphaClr(pi.penClr),  pi.penWidth))

            if (pi.showCoords):
                f.write("<g font-family=\"Verdana\" font-size=\"11\" fill=\"black\">\n\n")
                for p in pi.polygons:
                    cnt = len(p)
                    if cnt < 3: continue
                    for pt in p:
                        x = pt.x * invScale + offsetX
                        y = pt.y * invScale + offsetY
                        f.write("<text x=\"{0}\" y=\"{1}\">{2},{3}</text>\n".format(x, y, pt.x, pt.y))
                    f.write("\n")
                f.write("</g>\n")

        f.write("</svg>\n")
        f.close()
        return True