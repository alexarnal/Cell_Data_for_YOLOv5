import matplotlib.pyplot as plt
import numpy as np
import random
import shutil
import os
import re

def getCoordsFromSVG(fileName, svg_dpi=72, image_dpi=72):
    file = open(fileName,'r')
    fileContent = file.readline()
    file.close()
    fileContent = fileContent.split('>')
    X=[]
    Y=[]
    viewBox = 0
    for i,line in enumerate(fileContent): 
        coord = 0
        if 'viewBox=' in line:
            viewBox = re.search('viewBox="(.*)"', line)
        if 'circle' in line:
            x = re.search('cx="(.*)" cy', line)
            y = re.search('cy="(.*)" r', line)
            coord = [x.group(1),y.group(1)]
        else: continue
        X.append(float(coord[0]))
        Y.append(-float(coord[1]))
    coords = (np.vstack((np.array(X), np.array(Y))).T)*(image_dpi/svg_dpi)
    return coords, np.array(viewBox[1].split(' '), dtype='float')*(image_dpi/svg_dpi)

def getCoordsInFrame(coordinates, row, col, cellSize, frameSize):
    coords = coordinates[coordinates[:,0]>col]
    coords = coords[coords[:,0]<(col+frameSize)]
    coords = coords[coords[:,1]<(-row)]
    coords = coords[coords[:,1]>(-row-frameSize)]
    coords[:,0] = coords[:,0]-col
    coords[:,1] = coords[:,1]+row
    
    x_center = (coords[:,0])/frameSize
    y_center = -(coords[:,1])/frameSize
    width = cellSize/frameSize
    height = cellSize/frameSize
    
    return x_center, y_center, width, height
    
def saveCoordsTXT(c,x,y,w,h,fileName):   
    f = open(fileName+".txt", "w")
    for i in range(x.shape[0]):
        f.write("%d %f %f %f %f\n"%(c, x[i], y[i], w, h))
    f.close()

    
print("\nSet Up")    
dataDir = '../cell_detection/'
processedDir = dataDir+"processed/"
try:
    shutil.rmtree(processedDir)
except:
    print(processedDir, "does not exist")
os.mkdir(processedDir)
os.mkdir(processedDir+"images/")
os.mkdir(processedDir+"images/train/")
os.mkdir(processedDir+"images/valid/")
os.mkdir(processedDir+"labels/")
os.mkdir(processedDir+"labels/train/")
os.mkdir(processedDir+"labels/valid/")

from os import listdir
from os.path import isfile, join
onlyfiles = [os.path.splitext(f)[0] for f in listdir(dataDir+'cells') if isfile(join(dataDir+'cells', f)) and '.svg' in f]

for fileIndx,fileName in enumerate(onlyfiles):
    imageName = 'cells/'+fileName+'.png' 
    labelName = 'cells/'+fileName+'.svg' 
    temp = np.max(plt.imread(dataDir+imageName), axis=-1)
    image = np.zeros((temp.shape[0],temp.shape[1],3))
    for i in range(image.shape[2]): image[:,:,i] = temp 
    coordinates, viewBox = getCoordsFromSVG(dataDir+labelName, svg_dpi=72, image_dpi=300)

    print("\nSplitting & Saving Data")   
    locations = np.zeros(image.shape[0:2])
    trainImg = [] 
    trainMsk = [] 
    valImg = []
    valMsk = []
    frameSize = 256
    cellSize = 36
    stride = frameSize
    trainCount = 0
    valCount = 0
    validationPercentage = (1.0/3)
    for row in range(0, image.shape[0]-frameSize, stride):
        for col in range(0, image.shape[1]-frameSize, stride):
            frm = np.array([row,row+frameSize,col,col+frameSize]).astype('int')
            if random.random()>validationPercentage: 
                imageName = "images/train/%s_%s"%(fileIndx,trainCount)
                labelName = "labels/train/%s_%s"%(fileIndx,trainCount)
                locations[frm[0]:frm[1],frm[2]:frm[3]] += 1
                trainCount+=1
            else:
                imageName = "images/valid/%s_%s"%(fileIndx,valCount)
                labelName = "labels/valid/%s_%s"%(fileIndx,valCount)
                locations[frm[0]:frm[1],frm[2]:frm[3]] += 2
                valCount+=1
            
            x,y,w,h = getCoordsInFrame(coordinates, row, col, cellSize, frameSize)
            if (x.shape[0] ==0 and random.random()>0) or x.shape[0]>0:
                plt.imsave(processedDir + imageName + '.png',image[frm[0]:frm[1],frm[2]:frm[3]], cmap='gray')
                saveCoordsTXT(0, x, y, w, h, processedDir + labelName)
