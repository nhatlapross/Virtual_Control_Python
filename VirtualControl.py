import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np 
import cvzone
from pynput.keyboard import Key,Controller
import autopy

wCam=1200
hCam=800
frameR=280 #Frame Reduction
smoothening = 5

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

pTime = 0
plocX,plocY=0,0
clocX,clocY=0,0

wScr, hScr = autopy.screen.size()

detector = HandDetector(detectionCon=0.8)
keys=[["Q","W","E","R","T","Y","U","I","O","P","<<"],
	  ["A","S","D","F","G","H","J","K","L",";"],
	  ["Z","X","C","V","B","N","M",",",".","/"],
	  ["SPACE"]]
finalText=""
keyboard = Controller()


# def drawALL(img, buttonList):
# 	for button in buttonList:
# 		x,y = button.pos
# 		w,h = button.size
# 		cv2.rectangle(img,button.pos ,(x+w,y+h),(255,0,255),cv2.FILLED)
# 		cv2.putText(img,button.text,(x+12,y+58),cv2.FONT_HERSHEY_PLAIN,4,(255,255,255),4)
# 	return img

def drawALL(img, buttonList):
	imgNew = np.zeros_like(img,np.uint8)
	for button in buttonList:
		x,y = button.pos
		cvzone.cornerRect(imgNew,(button.pos[0],button.pos[1],button.size[0],button.size[1]),20,rt=0)
		cv2.rectangle(imgNew,button.pos,(x+button.size[0],y+button.size[1]),(255,0,255),cv2.FILLED)
		cv2.putText(imgNew,button.text,(x+12,y+58),cv2.FONT_HERSHEY_PLAIN,2,(255,255,255),3)

	out = img.copy()
	alpha = 0.5
	mask = imgNew.astype(bool)
	out[mask] = cv2.addWeighted(img,alpha,imgNew,1-alpha,0)[mask]
	return out

class Button():
	def __init__(self,pos,text,size=[70,70]):
		self.pos = pos
		self.size = size
		self.text = text
		
buttonList = []
for i in range(len(keys)):
		for j,key in enumerate(keys[i]):
			if i==3:
				buttonList.append(Button([80*j+i*120+20,80*i+20],key,[220,70]))
			else:
				buttonList.append(Button([80*j+i*20+20,80*i+20],key))

while True:
	success, img = cap.read()
	img = cv2.flip(img,1)
	hands, img = detector.findHands(img)
	

	if len(hands)==2:
		img = drawALL(img, buttonList)
		cv2.rectangle(img,(50,350),(750,450),(175,0,175),cv2.FILLED)
		cv2.putText(img,finalText,(60,425),cv2.FONT_HERSHEY_PLAIN,4,(255,255,255),4)
		# print(detector.fingersUp(hands[0]),detector.fingersUp(hands[1]))
		if detector.fingersUp(hands[0])[1] == 1:
			# print("Zoom")
			lmList1 = hands[0]["lmList"]
			lmList2 = hands[1]["lmList"]
			for button in buttonList:
				x, y = button.pos
				w, h = button.size

				if (x< lmList1[8][0]<x+w and y< lmList1[8][1]<y+h) or (x< lmList2[8][0]<x+w and y< lmList2[8][1]<y+h):
					cv2.rectangle(img,button.pos ,(x+w,y+h),(175,0,175),cv2.FILLED)
					cv2.putText(img,button.text,(x+12,y+58),cv2.FONT_HERSHEY_PLAIN,4,(255,255,255),4)
					l, _ = detector.findDistance(lmList1[8],lmList1[12])
					l2, _ = detector.findDistance(lmList2[8],lmList2[12])
					# print(l)

					# When clicked
					if l<30 or l2<30:
						cv2.rectangle(img,button.pos ,(x+w,y+h),(0,255,0),cv2.FILLED)
						cv2.putText(img,button.text,(x+12,y+58),cv2.FONT_HERSHEY_PLAIN,4,(255,255,255),4)
						try:
							if button.text=="<<":
								keyboard.press(Key.backspace)
								finalText = finalText[0:len(finalText)-1]
							elif button.text=="SPACE":
								keyboard.press(" ")
								finalText += " "
							else:
								keyboard.press(button.text)
								finalText += button.text
						except:
							pass
						# autopy.key.type_string(button.text,wpm=60)
						sleep(0.3)
	if len(hands)==1:
		lmList3 = hands[0]["lmList"]
		x1,y1 = lmList3[8][0:]
		x2,y2 = lmList3[12][0:]
		fingers = detector.fingersUp(hands[0])
		cv2.rectangle(img,(frameR-200,frameR-200),(wCam-frameR,hCam-frameR),(255,0,255),2)
		if fingers[1]==1 and fingers[2]==0:
			if frameR>=wCam:
				frameR=wCam
			if frameR>=hCam:
				frameR=hCam
			x3 = np.interp(x1*1.5,(frameR,wCam - frameR),(0,wScr))
			y3 = np.interp(y1*1.5,(frameR,hCam - frameR),(0,hScr))
			#6.Smoothen Values
			clocX = plocX +(x3 - plocX) / smoothening
			clocY = plocY +(y3 - plocY) / smoothening
			#7.Move Mouse
			autopy.mouse.move(clocX,clocY)
			cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
			plocX,plocY = clocX,clocY

		if fingers[1] == 1 and fingers[2] == 1:
            #9.Find distance betwwen fingers
			length, _ = detector.findDistance(lmList3[8],lmList3[12])
			# print(length)
            #10.Click mouse if distance short
			if length < 30:
				autopy.mouse.click()
				sleep(0.3)

	cv2.imshow("Image",img)
	key = cv2.waitKey(1)
	if key == ord('q'):
		break