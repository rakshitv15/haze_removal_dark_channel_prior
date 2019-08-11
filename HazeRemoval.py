import cv2
import numpy as np
import math

#represents a pixel of the image
class Pixel():
	def __init__(self,x,y,value):
		self.x=x
		self.y=y
		self.value=value

#calculates Dark Channel Prior based on patch size and omega
def getDCPrior(img,blockSize,w):
	if len(img.shape)!=3 and img.shape[2]!=3:
		print 'Please provide a BRG color image.'
		return None
	if blockSize % 2 == 0 or blockSize < 3:
		print 'blockSize is not odd or too small'
		return None
	imgMin = np.zeros((img.shape[0],img.shape[1]),dtype = np.uint8)
	minV = 255
	for i in range(0,img.shape[0]):
		for j in range(0,img.shape[1]):
			minV=255
			for k in range(0,3):
				if img.item(i,j,k)<minV:
					minV=img.item(i,j,k)
			imgMin[i,j]=minV
	edge=(blockSize-1)/2
	addedWidth=imgMin.shape[0]+2*edge
	addedHeight=imgMin.shape[1]+2*edge
	imgCanvas=np.zeros((addedWidth,addedHeight),dtype = np.uint8)
	imgCanvas[:,:] = 255
	imgCanvas[edge:addedWidth - edge,edge:addedHeight - edge] = imgMin
	imgDC = np.zeros((imgMin.shape[0],imgMin.shape[1]),np.uint8)
	minV = 255
	for i in range(edge,addedWidth-edge):
		for j in range(edge,addedHeight-edge):
			minV=255
			for k in range(i-edge,i+edge+1):
				for l in range(j-edge,j+edge+1):
					if imgCanvas.item((k,l)) < minV:
						minV = imgCanvas.item((k,l))
			imgDC[i-edge,j-edge] = minV
	return imgDC
 
 #determining atmospheric light
def getAtmLight(img,imgDC,p,maxAtmL):
#either maximum value can be considered as atmospheric light or the mean of the top values	
	if maxAtmL:
		meanAtml=False                     
	size=img.shape[0]*img.shape[1]
	topPixels=int(size*p)
	atmLight=0
	pixel_list = []
	for i in range(0,img.shape[0]):
		for j in range(0,img.shape[1]):
			pixel = Pixel(i,j,imgDC[i,j])
			pixel_list.append(pixel)
	pixel_list = sorted(pixel_list,key = lambda pixel:pixel.value,reverse=True)
	if topPixels == 0:
		for i in range(0,3):
			if img[pixel_list[0].x,pixel_list[0].y,i]>atmLight:
				atmLight = imgDC[pixel_list[0].x,pixel_list[0].y,i]
		return atmLight
#maximum value method
	if maxAtmL:
		for i in range(0,topPixels):
			for j in range(0,3):
				if img[pixel_list[i].x,pixel_list[i].y,j]>atmLight:
					atmLight = img[pixel_list[i].x,pixel_list[i].y,j]
		return atmLight
#mean value method
	if meanAtml:
		sum=0
		for i in range(0,topPixels):
			for j in range(0,3):
				sum = sum + img[pixel_list[i].x,pixel_list[i].y,j]
		atmLight = sum/(topPixels*3)
		return atmLight		

def deHaze(img,blockSize,w,p,maxAtmL,t0):
	imgDC=getDCPrior(img,blockSize,w)
	atmLight=getAtmLight(img,imgDC,p,maxAtmL)
	imgDC=np.float64(imgDC)
	transmission = 1 - w*imgDC/atmLight
	imgR=np.zeros(img.shape)
	for i in range(0,img.shape[0]):
		for j in range(0,img.shape[1]):
			if transmission[i,j]<t0:
				transmission[i,j]=t0
	for i in range(0,3):
		img=np.float64(img)
		imgR[:,:,i] = (img[:,:,i]-atmLight)/transmission + atmLight
		for j in range(0,img.shape[0]):
			for k in range(0,img.shape[1]):
				if imgR[j,k,i] > 255:
					imgR[j,k,i] = 255
				if imgR[j,k,i] < 0:
					imgR[j,k,i] = 0
	imgR = np.uint8(imgR)
	return imgR			

#below code can be adjusted to take desired images as input and write the output as well
for i in range(1,9):				
	img=cv2.imread('/home/rakshit/65/Input/%s.png'%(i),cv2.IMREAD_COLOR)
	imgR=deHaze(img,15,0.95,0.001,True,0.1)
	cv2.imwrite('/home/rakshit/65/Output/DeHazed_%s.jpg'%(i),imgR)
cv2.waitKey(0)
cv2.destroyAllWindows()