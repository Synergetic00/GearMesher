from PIL import Image
import numpy as np
from tkinter import filedialog

gearRatio = 9
gearOverlap = 1.0
computationSteps = 100

def loadGearImage():
    filename = filedialog.askopenfilename()
    image = Image.open(filename).convert('L')
    image.load()
    data = np.asarray(image)
    return data

def getBlackPixels(image, offset):
    rows = len(image)
    cols = len(image[0])
    size = max([rows, cols])
    scale = 2./size
    coords =  []
    for row in range(rows):
        for col in range(cols):
            if image[row][col] == 0:
                x = scale*(col - (cols-1)/2.) + offset[0]
                y = scale*(row - (rows-1)/2.) + offset[1]
                coords += [(x, y)]
    return coords, size


def outputGearImage(image, coords, size, ratio):
    '''Draws coordinates as pixels on image'''
    newImage = image
    for (x,y) in coords:
        row = int(np.floor((y+ratio)*size/(2*ratio)))
        col = int(np.floor((x+ratio)*size/(2*ratio)))
        try:
            newImage[row][col] = 255.0
        except:
            pass
    return newImage
    
def rotatePts(points, axis, theta):
    uncentered = [(((x - axis[0])*np.cos(theta) - (y - axis[1])*np.sin(theta)) + axis[0], ((x - axis[0])*np.sin(theta) + (y-axis[1])*np.cos(theta)) + axis[1]) for (x,y) in points]
    return uncentered

def writeOutputGear(gear,filename):
    img = Image.fromarray(gear)
    img = img.convert('RGB')
    img.save(filename)
    return None

def dist(x, y):
    return np.sqrt(x*x+y*y)

def outputCleanup(image):
    '''Remove the 'halo' around output image; adds a mark indicating the center
    TODO: maybe apply median filter?'''
    newImage = image
    size = len(image) # Should be same number of rows/columns
    radius = size/2.
    for row in range(size):
        for col in range(size):
            if dist(row-radius, col-radius) >= radius-.5:
                newImage[row][col] = 255.0
    # Mark the center
    markRadius = np.max([2., size/200.]) # How big to make the mark
    for i in range(50):
        theta = i*2*np.pi/50
        x = int(np.round(radius + markRadius*np.cos(theta)))
        y = int(np.round(radius + markRadius*np.sin(theta)))
        newImage[y][x] = 255.0
    return newImage

def drawCrossbar(distance):
    distance = int(distance) # just in case
    '''Draws the image of the crossbar that holds the two gear axles'''
    # Size of the image:
    height = int(np.round(distance/6.))
    width = int(np.ceil(distance*7./6))
    # Coordinates of the axle holes' centers:
    radius = height/2. - 0.5
    holeOne = (radius, radius)
    holeTwo = (distance+radius, radius)
    # Draw the crossbar:
    crossbarImage = 255.0*np.ones((height, width))
    crossbarImage[(0, height-1), int(np.ceil(holeOne[0])):int(np.floor(holeTwo[0])+1)] = 0.
    for i in range(distance):
        theta = np.pi*i/distance - np.pi/2
        rows = (int(np.round(holeOne[1] - radius*np.sin(theta))), int(np.round(holeTwo[1] + radius*np.sin(theta))))
        cols = (int(np.round(holeOne[0] - radius*np.cos(theta))), int(np.round(holeTwo[0] + radius*np.cos(theta))))
        crossbarImage[rows, cols] = 0.0
    # Draw crossbar holes
    markRadius = np.max([2., distance/200.]) # How big to make the mark
    for i in range(50):
        theta = i*2*np.pi/50
        x = int(np.round(holeOne[0] + markRadius*np.cos(theta)))
        y = int(np.round(holeOne[1] + markRadius*np.sin(theta)))
        crossbarImage[y][x] = 0.
        crossbarImage[y][x+distance] = 0.
    return crossbarImage

inputGear = loadGearImage()
offset = (gearRatio+1-gearOverlap, 0)
inputCoords, inputImageSize = getBlackPixels(inputGear, offset)
outputImageSize = inputImageSize*gearRatio
outputGear = np.zeros([outputImageSize, outputImageSize])
theta = 2*np.pi/computationSteps
phi = 2*np.pi/(computationSteps*gearRatio)
for step in range(computationSteps):
    coords = rotatePts(inputCoords, offset, theta*step)
    addPoints = []
    for coord in coords:
        if dist(*coord)<gearRatio:
            addPoints += [coord]
    # Rotate the points that contribute to the output gear's profile
    for extraRotation in range(gearRatio):
        rotateBy = phi*step + 2*np.pi*extraRotation/gearRatio
        addPointsRot = rotatePts(addPoints, (0,0), rotateBy)
        # Convert those points into pixels, draw on output gear
        outputGear = outputGearImage(outputGear, addPointsRot, outputImageSize, gearRatio)
    print('Progress: {}/{}'.format(step, computationSteps)) # Debug
# Clean up image
outputGear = outputCleanup(outputGear)
# Should also make little marks for centroids and distances
# Animate?
# Save image
outFilename = filedialog.asksaveasfilename(defaultextension='.png', initialfile='gear_output')
writeOutputGear(outputGear, outFilename)
# save the crossbar image too
crossbar = drawCrossbar(inputImageSize*(gearRatio+1-gearOverlap)/2)
outFilename = filedialog.asksaveasfilename(defaultextension='.png', initialfile='crossbar')
writeOutputGear(crossbar, outFilename)