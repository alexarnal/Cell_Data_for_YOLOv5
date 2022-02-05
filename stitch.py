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
    #fileContent = fileContent.split('\n')
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
dataDir = sys.argv[1]
processedDir = dataDir+"stitched/"
try:
    shutil.rmtree(processedDir)
except:
    print(processedDir, "does not exist")
os.mkdir(processedDir)

print("\nLoading Data") 
imageName = sys.argv[2] 
temp = plt.imread(dataDir+imageName)[:,:,1] #green channel
image = np.zeros((temp.shape[0],temp.shape[1],3))
image[:,:,0]=temp
image[:,:,1]=temp
image[:,:,2]=temp
canvas = np.zeros((temp.shape[0],temp.shape[1],3))
 
#imageFolder = 'images' #listdir(dataDir)
labelFolder = 'exp/labels/'

#onlyImgFiles = [f for f in os.listdir(dataDir+imageFolder) if os.path.isfile(os.path.join(dataDir+imageFolder, f))]
#onlyImgFiles.sort(key=lambda f: int(re.sub('\D', '', f)))

onlyLblFiles = [f for f in os.listdir(dataDir+labelFolder) if os.path.isfile(os.path.join(dataDir+labelFolder, f))]
onlyLblFiles.sort(key=lambda f: int(re.sub('\D', '', f)))


print("\nStitching based on reference image")   
frameSize = 256
cellSize = 36
stride = frameSize
indx = 0
imageDims = [image.shape[1],image.shape[0]]
startSVG(processedDir + "stitched",imageDims)
for row in range(0, image.shape[0]-frameSize, stride):
    for col in range(0, image.shape[1]-frameSize, stride):
        if os.path.isfile(dataDir+labelFolder+str(indx)+".txt") == False: 
            indx+=1
            continue
        frm = np.array([row,row+frameSize,col,col+frameSize]).astype('int')
        #labelName = "labels/train/%s"%trainCount
        #canvas[frm[0]:frm[1],frm[2]:frm[3]] += plt.imread(dataDir+'images/'+str(indx)+".png")
        #trainCount+=1
        c,x,y,w,h,conf=getYOLODataFromTXT(dataDir+labelFolder+str(indx)+".txt",frameSize)
        
        #account for relative position of patch in large image
        x += col
        y += row
        #saveCoordsTXT(c, x, y, w, h, processedDir + "stitched",indx)
        saveCoordsSVG(x, y, processedDir + "stitched",indx)
        indx+=1
    #if valCount == 10: break
endSVG(processedDir + "stitched")

print("Done!")
