import matplotlib.pyplot as plt
import numpy as np
import shutil
import sys
import os
import re

def getYOLODataFromTXT(fileName,scale):
    file = open(fileName,'r')
    fileContent = file.readlines()
    file.close()
    cl,x,y,w,h,conf = [],[],[],[],[],[]
    for i,line in enumerate(fileContent): 
        if line == "": continue
        #print(line.split(' '))
        cl.append(int(line.split(' ')[0]))
        x.append(float(line.split(' ')[1])*scale)
        y.append(float(line.split(' ')[2])*scale)
        w.append(float(line.split(' ')[3])*scale)
        h.append(float(line.split(' ')[4])*scale)
        conf.append(float(line.split(' ')[5]))
    return np.array(cl), np.array(x), np.array(y), np.array(w), np.array(h), np.array(conf)

def startSVG(fileName,dims):
    f = open(fileName+".svg", "w")
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s">\n'%(dims[0], dims[1]))
    f.write('<rect width="%s" height="%s" style="fill:none"/>\n'%(dims[0], dims[1]))
    f.close()

def saveCoordsSVG(x,y,fileName,indx): 
    f = open(fileName+".svg", "a")
    for i in range(x.shape[0]):
        f.write('<circle cx="%s" cy="%s" r="%s" style="fill:#000000"/>\n'%(x[i], y[i], 3))
    f.close()

def endSVG(fileName):
    f = open(fileName+".svg", "a")
    f.write('</svg>')
    f.close()    
    
print("\nSet Up")  
dataDir = "/"
processedDir = dataDir+"stitched/"
try:
    shutil.rmtree(processedDir)
except:
    print(processedDir, "does not exist")
os.mkdir(processedDir)

print("\nLoading Data") 
labelFolder = 'labels/'
onlyLblFiles = [f for f in os.listdir(dataDir+labelFolder) if os.path.isfile(os.path.join(dataDir+labelFolder, f))]
onlyLblFiles.sort(key=lambda f: int(re.sub('\D', '', f)))


print("\nStitching based on reference image")   
frameSize = 256
cellSize = 36
stride = frameSize
indx = 0
imageDims = [8350,5577]
startSVG(processedDir + "stitched",imageDims)
for row in range(0, imageDims[1]-frameSize, stride):
    for col in range(0, imageDims[0]-frameSize, stride):
        if os.path.isfile(dataDir+labelFolder+str(indx)+".txt") == False: 
            indx+=1
            continue
        frm = np.array([row,row+frameSize,col,col+frameSize]).astype('int')
        c,x,y,w,h,conf=getYOLODataFromTXT(dataDir+labelFolder+str(indx)+".txt",frameSize)
        x += col #account for relative position of patch in large image
        y += row
        saveCoordsSVG(x, y, processedDir + "stitched",indx)
        indx+=1
endSVG(processedDir + "stitched")

print("Done!")
