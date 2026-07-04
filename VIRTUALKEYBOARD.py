import cv2
import mediapipe as mp
import numpy as np
import time
from xray_predictor import predict_xray, upload_xray

########################################
# Keyboard Layout
########################################

keys = [
["Q","W","E","R","T","Y","U","I","O","P"],
["A","S","D","F","G","H","J","K","L"],
["Z","X","C","V","B","N","M"],
["SPACE","BACKSPACE","CLEAR","ENTER"]
]

class Button():
    def __init__(self,pos,text):

        self.pos = pos
        self.text = text

        if text == "SPACE":
            self.size = [300,85]
        elif text in ["BACKSPACE","CLEAR","ENTER"]:
            self.size = [200,85]
        else:
            self.size = [85,85]


########################################
# Create Keyboard Buttons
########################################

buttonList = []

for i in range(len(keys)):
    for j,key in enumerate(keys[i]):

        if key == "SPACE":
            pos_x = 390
        elif key == "BACKSPACE":
            pos_x = 700
        elif key == "CLEAR":
            pos_x = 910
        elif key == "ENTER":
            pos_x = 1120
        else:
            pos_x = 100*j + 50

        pos_y = 100*i + 50
        buttonList.append(Button([pos_x,pos_y],key))


########################################
# Mediapipe Hand Setup
########################################

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils


########################################
# Camera Setup
########################################

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

finalText = ""
user_name = ""
start_xray = False

clickTime = 0
cooldown = 0.5


########################################
# Main Loop
########################################

while True:

    success,img = cap.read()
    img = cv2.flip(img,1)

    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)


    ########################################
    # Draw Keyboard
    ########################################

    for button in buttonList:

        x,y = button.pos
        w,h = button.size

        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),cv2.FILLED)

        cv2.putText(img,button.text,(x+20,y+60),
        cv2.FONT_HERSHEY_PLAIN,2,(255,255,255),2)


    ########################################
    # Hand Detection
    ########################################

    if results.multi_hand_landmarks:

        for handLms in results.multi_hand_landmarks:

            mpDraw.draw_landmarks(img,handLms,mpHands.HAND_CONNECTIONS)

            lmList = []

            for id,lm in enumerate(handLms.landmark):

                h,w,c = img.shape
                cx,cy = int(lm.x*w),int(lm.y*h)

                lmList.append((cx,cy))


            if lmList:

                x1,y1 = lmList[8]    # index finger
                x2,y2 = lmList[12]   # middle finger

                distance = ((x2-x1)**2 + (y2-y1)**2)**0.5


                for button in buttonList:

                    x,y = button.pos
                    w,h = button.size

                    if x < x1 < x+w and y < y1 < y+h:

                        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),cv2.FILLED)

                        cv2.putText(img,button.text,(x+20,y+60),
                        cv2.FONT_HERSHEY_PLAIN,2,(255,255,255),2)


                        currentTime = time.time()

                        if distance < 40 and currentTime-clickTime > cooldown:

                            if button.text == "SPACE":

                                finalText += " "

                            elif button.text == "BACKSPACE":

                                finalText = finalText[:-1]

                            elif button.text == "CLEAR":

                                finalText = ""

                            elif button.text == "ENTER":

                                user_name = finalText

                                # Upload X-ray image
                                image_path = upload_xray()

                                if image_path:
                                    result = predict_xray(image_path)
                                else:
                                    result = "NO IMAGE SELECTED"

                                finalText = result
                                start_xray = True

                            else:

                                finalText += button.text

                            clickTime = currentTime


    ########################################
    # Display Typed Text
    ########################################

    cv2.rectangle(img,(50,450),(1200,520),(175,0,175),cv2.FILLED)

    cv2.putText(img,finalText[-40:],(60,500),
    cv2.FONT_HERSHEY_PLAIN,3,(255,255,255),3)


    ########################################
    # Show Prediction Result
    ########################################

    if start_xray:

        cv2.putText(img,"User: "+user_name,(50,580),
        cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

        cv2.putText(img,"Result: "+finalText,(50,620),
        cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)


    cv2.imshow("Virtual Keyboard + XRay Detection",img)

    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()