import pygame
import sys
import cv2 as cv
import threading
import os
import time
from qreader import QReader
import RPi.GPIO as GPIO


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import serial

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
ser.close()

ser2 = serial.Serial('/dev/ttyACM0', 9600)
ser2.close()
serClose = True

databaseURL = 'https://fileuploading-67153-default-rtdb.asia-southeast1.firebasedatabase.app' 


cred = credentials.Certificate("fileuploading-67153-firebase-adminsdk-gn9up-59b2c4b6b9.json")
default_app = firebase_admin.initialize_app(cred, {
	'databaseURL':databaseURL
	})

APPWIDTH, APPHEIGHT = 1024, 600 
FPS = 60
pygame.init()
pygame.display.set_caption("Final System")
sensorActivated = False
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
# cap = cv.VideoCapture(-1, cv.CAP_V4L)
coinRead = 0


#GPIO
servoButA = 26
servoButB = 32
extraButC = 37

relIn1 = 8
relIn2 = 10
relIn3 = 12

motInA = 16
motInB = 18
enA = 38
enB = 40

limSwA = 22
limSwB = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(servoButA, GPIO.OUT)
GPIO.setup(servoButB, GPIO.OUT)
GPIO.setup(extraButC, GPIO.OUT)

GPIO.setup(relIn1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(relIn2, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(relIn3, GPIO.OUT, initial=GPIO.HIGH)

GPIO.setup(limSwA, GPIO.IN)
GPIO.setup(limSwB, GPIO.IN)

GPIO.setup(motInA, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motInB, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(enA, GPIO.OUT)
GPIO.setup(enB, GPIO.OUT)
pwmA = GPIO.PWM(enA, 1000)
pwmB = GPIO.PWM(enB, 1000)
pwmA.start(45)
pwmB.start(45)





Black = (0,0,0)
White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Blue = (0, 0, 255)

timerTick = 0
idleTimer = 10
idleTimerStr = "10"

topEndTick = 0
rfidInitTick = 0
ticketScanInitTick=0
delayerTick = 0
delayerTickState = False
printEndTick = 0

coinBlit = "0"
prevBlitVal = 0
blitVal = "0"

def blitter(serRead):
    global coinBlit

    if serRead != "":
        coinBlit = serRead
    
    if len(coinBlit) < 1:
        coinBlit = "00"
        
    return coinBlit

#ASSET DECLARATIONS

mainMenu = pygame.transform.scale(pygame.image.load('guiAssets/1.jpg'), (APPWIDTH,APPHEIGHT))
ticketScanned = pygame.transform.scale(pygame.image.load('guiAssets/2.jpg'), (APPWIDTH,APPHEIGHT))
nowPrinting = pygame.transform.scale(pygame.image.load('guiAssets/3.jpg'), (APPWIDTH,APPHEIGHT))
getDocuPrompt = pygame.transform.scale(pygame.image.load('guiAssets/4.jpg'), (APPWIDTH,APPHEIGHT))
onHoldCoin = pygame.transform.scale(pygame.image.load('guiAssets/5.jpg'), (APPWIDTH,APPHEIGHT))
onHoldTap = pygame.transform.scale(pygame.image.load('guiAssets/6.jpg'), (APPWIDTH,APPHEIGHT))
topUpMode = pygame.transform.scale(pygame.image.load('guiAssets/7.jpg'), (APPWIDTH,APPHEIGHT))
topUpSuccess = pygame.transform.scale(pygame.image.load('guiAssets/8.jpg'), (APPWIDTH,APPHEIGHT))
coinTimeOut = pygame.transform.scale(pygame.image.load('guiAssets/9.jpg'), (APPWIDTH,APPHEIGHT))
maintenancePage = pygame.transform.scale(pygame.image.load('guiAssets/10.jpg'), (APPWIDTH,APPHEIGHT))

#FONTS 
dfont = pygame.font.SysFont('impact', 50)
qrFont = pygame.font.SysFont('impact', 40)
topUpFont = pygame.font.SysFont('impact',60)


def shortDispenser(paperAmt):

    print(f"paperAmount= {paperAmt}")
    for x in range(paperAmt):
        GPIO.output(servoButA, GPIO.HIGH)
        GPIO.output(servoButB, GPIO.HIGH)
        GPIO.output(extraButC, GPIO.HIGH)
        print("dispense")
        time.sleep(2.2)
        print("Close")
        GPIO.output(servoButA, GPIO.LOW)
        GPIO.output(servoButB, GPIO.HIGH)
        GPIO.output(extraButC, GPIO.LOW)
        print(x)
        time.sleep(2)

def longDispenser(paperAmt):

    for x in range(paperAmt):
        GPIO.output(servoButA, GPIO.HIGH)
        GPIO.output(servoButB, GPIO.HIGH)
        GPIO.output(extraButC, GPIO.HIGH)
        print("dispense")
        time.sleep(.5)
        print("Close")
        GPIO.output(servoButA, GPIO.LOW)
        GPIO.output(servoButB, GPIO.HIGH)
        GPIO.output(extraButC, GPIO.LOW)
        print(x)
        time.sleep(2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((APPWIDTH, APPHEIGHT),pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.stateManager = stateManager('scene1')
        self.scene1 = scene1(self.screen, self.stateManager)
        self.scene2 = scene2(self.screen, self.stateManager)
        self.scene3 = scene3(self.screen, self.stateManager)
        self.scene4 = scene4(self.screen, self.stateManager)
        self.scene5 = scene5(self.screen, self.stateManager)
        self.scene6 = scene6(self.screen, self.stateManager) 
        self.scene7 = scene7(self.screen, self.stateManager)
        self.scene8 = scene8(self.screen, self.stateManager)
        self.scene9 = scene9(self.screen, self.stateManager)
        self.scene10 = scene10(self.screen, self.stateManager)

        self.states = {'scene1': self.scene1, 'scene2': self.scene2, 'scene3': self.scene3
                        , 'scene4': self.scene4, 'scene5': self.scene5, 'scene6': self.scene6, 'scene7': self.scene7, 'scene8': self.scene8,
                        'scene9': self.scene9, 'scene10': self.scene10}

    def run(self):
        while True:
            mouse = pygame.mouse.get_pos()
            clicker = pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.states[self.stateManager.getState()].run(mouse,clicker)

            # print(mouse)
            # print(counter)

            pygame.display.update()
            self.clock.tick(FPS)

class scene1:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):
        global decoded_text
        global delayerTick
        # global cap

        self.display.blit(mainMenu,(0,0))
        cap = cv.VideoCapture(-1, cv.CAP_V4L)

        if not cap.isOpened():
            print("No cam detected")
            exit()

        ret, frame = cap.read()
        if not ret:
            print("No frames Returned")

        # try:
        #     cropped = frame[160:240, 320:400]
        # except:
        #     ret, frame = cap.read()
        #     time.sleep(2)
        
        cropped = frame[160:240, 320:400]
        resized = cv.resize(cropped,(300,300))
        resized = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)
        cv.rectangle(frame,(240,160),(400,320),(0,0,255),1)
        cropped = cv.rotate(cropped, cv.ROTATE_90_COUNTERCLOCKWISE)
        cropped = cv.resize(cropped,(300,300))
        pyFrame = pygame.surfarray.make_surface(cropped)
        ref1= resized[42,42]
        ref4= resized[42, 70]
        self.display.blit(pyFrame,(560,150))

        if int(ref1) <= 100 and int(ref4) >= 150:
            try: 
                cv.imwrite('qrRead.jpg', frame)
                decoded_text = QReader().detect_and_decode(image=frame)
                print(decoded_text[0])
                qrTicket = qrFont.render(decoded_text[0], 0, Green)
                self.display.blit(qrTicket, (425,485, 100, 50))
                self.stateManager.setState('scene2')
            except:
                print("error in qr")

        else:
            noQR = dfont.render("No QR Detected", 0, Red)
            self.display.blit(noQR, (480,480, 100, 50))
        


class scene2:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager
        self.clock = pygame.time.Clock()

    def run(self, mouse, clicker):
        self.display.blit(ticketScanned,(0,0))
        global blitVal
        global coinBlit
        global ticketScanInitTick

        ticketScanInitTick+=1

        if ticketScanInitTick > 100:
            try:
                ticketValue = decoded_text[0]
                global ref
                ref = db.reference(f"/transaction/{ticketValue}")
                print(f"this is the path: /transaction/{ticketValue}")
                #ref.child("name").get()
                transactionStatus = ref.child("status").get()

                if transactionStatus == "pending":
                    ref.update({"status":"scanned"})
                    transactionType = ref.child("transactionType").get()

                    if transactionType == "printing":
                        print("For printing")

                        global printParams

                        printParams = [ref.child("colortype").get(),
                                    ref.child("papersize").get(),
                                    ref.child("paymenttype").get(),
                                    ref.child("totalPages").get(),
                                    ref.child("totalPrice").get(),
                                    ref.child("name").get(),
                                    ref.child("url").get(),
                                    ref.child("userID").get()]
                        
                        if printParams[2] == "OnlinePayment":
                            print("online!")
                            global onUserParams
                            global onUserRef
                            blitVal = "0"
                            coinBlit = "0"
                            onUserRef = db.reference(f"/userData/{ref.child("userID").get()}")
                            print(ref.child("userID").get())
                            onUserParams = [ onUserRef.child("balance").get(), onUserRef.child("email").get()]
                            self.stateManager.setState('scene3')

                        elif printParams[2] == "TapID":
                            print("RFID")

                            self.display.blit(onHoldTap,(0,0))        

                            coinValText = topUpFont.render(str(printParams[4]), 0, Red)
                            self.display.blit(coinValText, (670,300))
                                
                            self.stateManager.setState('scene6')
                        
                        elif printParams[2] == "Coin":
                            print("Coin payment")
                            global coinUserParams
                            global coinUserRef
                            blitVal = "0"
                            coinBlit = "0"
                            coinUserRef = db.reference(f"/userData/{ref.child("userID").get()}")
                            print(ref.child("userID").get())
                            coinUserParams = [ coinUserRef.child("balance").get(), coinUserRef.child("email").get()]
                            ser.open()
                            self.stateManager.setState('scene5')
            
                    elif transactionType == "top-up":
                        print("For Top up")
                        global topUpParams
                        global topUpRef
                        blitVal = "0"
                        coinBlit = "0"
                        topUpRef = db.reference(f"/userData/{ref.child("userID").get()}")

                        topUpParams = [ topUpRef.child("balance").get(), topUpRef.child("email").get()]

                        self.display.blit(topUpMode,(0,0))
                        ser.open()
                        self.stateManager.setState('scene7')
                    else:
                        print("invalid Code")

                else:
                    print("No transaction Type")
                    print(ref.child("transactionStatus").get())
                    self.stateManager.setState('scene1')

            except Exception as error:
                print("INVALID TICKET")
                print(error)
                self.stateManager.setState('scene1')


        

class scene3:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):
        self.display.blit(nowPrinting,(0,0)) 

        if printParams[1] == "short" and printParams[0] == "bnw":
            print("short and BnW!")
            GPIO.output(relIn2, GPIO.LOW)
            GPIO.output(servoButB, GPIO.LOW)
            GPIO.output(servoButA, GPIO.HIGH)
            GPIO.output(extraButC, GPIO.LOW)

            printerName = "shortBond_bnw"
            
            fileName = "queued.pdf"

            os.system(f"wget -O {fileName} {printParams[6]}")

            if GPIO.input(limSwA) == 0:
                pwmA.ChangeDutyCycle(50)
                pwmB.ChangeDutyCycle(50)
                GPIO.output(motInA, GPIO.LOW)
                GPIO.output(motInB, GPIO.HIGH)

            else:
                GPIO.output(motInA, GPIO.LOW)
                GPIO.output(motInB, GPIO.LOW)
                shortDispenser(int(printParams[3]))
                time.sleep(3)
                GPIO.output(relIn2, GPIO.HIGH)
                os.system(f"lp -d {printerName} {fileName}")
                
                print("printing...")
                printParams[1] = "dataCleared"

        elif printParams[1] == "short" and printParams[0] == "colored":

            print("short and Colored!")
            GPIO.output(relIn2, GPIO.LOW)

            printerName = "shortBond_color"
            
            fileName = "queued.pdf"

            os.system(f"wget -O {fileName} {printParams[6]}")

            if GPIO.input(limSwA) == 0:
                pwmA.ChangeDutyCycle(45)
                pwmB.ChangeDutyCycle(45)
                GPIO.output(motInA, GPIO.LOW)
                GPIO.output(motInB, GPIO.HIGH)
    
                GPIO.output(servoButB, GPIO.LOW)
                GPIO.output(servoButA, GPIO.HIGH)
                GPIO.output(extraButC, GPIO.LOW)

            else:
                GPIO.output(motInA, GPIO.LOW)
                GPIO.output(motInB, GPIO.LOW)
                shortDispenser(int(printParams[3]))
                time.sleep(3)
                GPIO.output(relIn2, GPIO.HIGH)
                os.system(f"lp -d {printerName} {fileName}")

                print("printing...")
                printParams[1] = "dataCleared"

        elif printParams[1] == "long" and printParams[0] == "bnw":
            print("long and BnW!")
            GPIO.output(relIn3, GPIO.LOW)
            GPIO.output(servoButB, GPIO.LOW)
            GPIO.output(servoButA, GPIO.HIGH)
            GPIO.output(extraButC, GPIO.LOW)

            printerName = "longBond_bnw"
            
            fileName = "queued.pdf"

            os.system(f"wget -O {fileName} {printParams[6]}")

            if GPIO.input(limSwB) == 0:
                pwmA.ChangeDutyCycle(45)
                pwmB.ChangeDutyCycle(45)
                GPIO.output(motInA, GPIO.HIGH)
                GPIO.output(motInB, GPIO.LOW)

            else:
                GPIO.output(motInA, GPIO.LOW)
                GPIO.output(motInB, GPIO.LOW)
                longDispenser(int(printParams[3]))
                time.sleep(3)
                GPIO.output(relIn3, GPIO.HIGH)
                os.system(f"lp -d {printerName} {fileName}")
                
                print("printing...")
                printParams[1] = "dataCleared"
        elif printParams[1] == "long" and printParams[0] == "colored":
            print("long and colored!")
            GPIO.output(relIn3, GPIO.LOW)
            GPIO.output(servoButB, GPIO.LOW)
            GPIO.output(servoButA, GPIO.HIGH)
            GPIO.output(extraButC, GPIO.LOW)

            printerName = "longBond_color"
            
            fileName = "queued.pdf"

            os.system(f"wget -O {fileName} {printParams[6]}")

            if GPIO.input(limSwB) == 0:
                pwmA.ChangeDutyCycle(45)
                pwmB.ChangeDutyCycle(45)
                GPIO.output(motInA, GPIO.HIGH)
                GPIO.output(motInB, GPIO.LOW)

            else:
                GPIO.output(motInA, GPIO.LOW)
                GPIO.output(motInB, GPIO.LOW)
                longDispenser(int(printParams[3]))
                time.sleep(3)
                GPIO.output(relIn3, GPIO.HIGH)
                os.system(f"lp -d {printerName} {fileName}")
                
                print("printing...")
                printParams[1] = "dataCleared"          


        else:
            print("Printing done!")
            self.stateManager.setState('scene4')
            
class scene4:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):
        self.display.blit(getDocuPrompt,(0,0))

        global printEndTick

        printEndTick+=1

        if printEndTick >= 180:
            self.stateManager.setState('scene1')
        
class scene5:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):
        self.display.blit(onHoldCoin,(0,0))
        global idleTimer
        global timerTick
        global idleTimerStr
        global prevBlitVal
        global blitVal
        global delayerTick

    
        
        GPIO.output(servoButB, GPIO.HIGH)
        GPIO.output(servoButA, GPIO.LOW)
        GPIO.output(extraButC, GPIO.HIGH)

        GPIO.output(relIn1, GPIO.LOW)

        coinVal = ser.read(2)
        coinRead = coinVal.decode("utf-8")

        blitVal = blitter(coinRead)
        blitValInt = int(blitVal)

        coinValText = topUpFont.render(str(printParams[4]), 0, Red)
        self.display.blit(coinValText, (570,190))

        if prevBlitVal != blitValInt:
            idleTimer = 11
            prevBlitVal = blitValInt


        
        # if printParams[4] <= blitValInt:
        #     delayerTick+=1

        #     if delayerTick > 120:
        #         coinChange = blitValInt - printParams[4]
        #         totalBal = coinChange + coinUserParams[0]
        #         coinUserRef.update({"balance":totalBal})
        #         idleTimer = 11 
        #         blitValInt = 0
        #         blitVal = "0"
        #         ser.close()
        #         GPIO.output(relIn1, GPIO.HIGH)
        #         GPIO.output(servoButB, GPIO.LOW)
        #         GPIO.output(servoButA, GPIO.HIGH)
        #         GPIO.output(extraButC, GPIO.HIGH)  
        #         delayerTick = 0             
        #         self.stateManager.setState('scene3')
                


        coinValText = topUpFont.render(blitVal, 0, Red)
        self.display.blit(coinValText, (680,380))
        print(blitVal)

        timerTick += 1

        if timerTick > 60:
            timerTick = 0
            idleTimer -= 1
            idleTimerStr = str(idleTimer)

        if idleTimer < 1:
            
            GPIO.output(relIn1, GPIO.HIGH)

            if printParams[4] <= blitValInt:
                delayerTick+=1

                if delayerTick > 120:

                    coinChange = blitValInt - printParams[4]
                    totalBal = coinChange + coinUserParams[0]
                    coinUserRef.update({"balance":totalBal})
                    idleTimer = 11 
                    blitValInt = 0
                    blitVal = "0"
                    ser.close()
                    GPIO.output(relIn1, GPIO.HIGH)
                    GPIO.output(servoButB, GPIO.LOW)
                    GPIO.output(servoButA, GPIO.HIGH)
                    GPIO.output(extraButC, GPIO.HIGH)  
                    delayerTick = 0             
                    self.stateManager.setState('scene3')
            else:       

                coinUserRef.update({"balance":int(coinUserParams[0]) + blitValInt})
                idleTimer = 11 
                blitValInt = 0
                GPIO.output(relIn1, GPIO.HIGH)
                ser.close()
                GPIO.output(servoButB, GPIO.LOW)
                GPIO.output(servoButA, GPIO.HIGH)
                GPIO.output(extraButC, GPIO.HIGH)
                self.stateManager.setState('scene9')




        
        timer = topUpFont.render(f'Idle Timer: {idleTimerStr}', 0, Red)
        self.display.blit(timer, (340,540))




class scene6:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):

        global serClose

        self.display.blit(onHoldTap,(0,0))        

        coinValText = topUpFont.render(str(printParams[4]), 0, Red)
        self.display.blit(coinValText, (670,300))


        

        global rfidInitTick

        rfidInitTick += 1
        if serClose:       
            ser2.open()
            serClose = False

        GPIO.output(servoButB, GPIO.HIGH)
        GPIO.output(servoButA, GPIO.HIGH)
        GPIO.output(extraButC, GPIO.LOW)

        if rfidInitTick > 200:
            
            rfidScanned = ser2.read(8)
            rfidString = rfidScanned.decode("utf-8")

            rfidRef = db.reference(f'/rfidData/{rfidString}')

            affiliationString = rfidRef.child("affiliation").get()

            if affiliationString == "Adamson":
                print("idScanned")
                print(f'transaction cost = {rfidRef.child("studentName").get()}')
                rfStudentName = rfidRef.child("studentName").get()

                billedTo = topUpFont.render(f"billed to :{rfStudentName}", 0, Red)
                self.display.blit(billedTo, (350,380))  

                creditDue = printParams[4]
                currentCreds = int(rfidRef.child("credit").get())
                transacCred = creditDue + currentCreds
                rfidRef.update({"credit":transacCred})
                
                
                ser2.close()
                serClose = True
                self.stateManager.setState('scene3')



        
class scene7:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):
        global idleTimer
        global timerTick
        global idleTimerStr
        global prevBlitVal
    
        
        GPIO.output(servoButB, GPIO.HIGH)
        GPIO.output(servoButA, GPIO.LOW)
        GPIO.output(extraButC, GPIO.HIGH)

        GPIO.output(relIn1, GPIO.LOW)

        self.display.blit(topUpMode,(0,0))

        coinVal = ser.read(2)
        coinRead = coinVal.decode("utf-8")
        # print(coinRead)

        blitVal = blitter(coinRead)
        blitValInt = int(blitVal)


        if prevBlitVal != blitValInt:
            idleTimer = 11
            prevBlitVal = blitValInt

        coinValText = topUpFont.render(f"{blitVal}", 0, Red)
        self.display.blit(coinValText, (690,250))

        timerTick += 1

        if timerTick > 60:
            timerTick = 0
            idleTimer -= 1
            idleTimerStr = str(idleTimer)

        if idleTimer < 0:
            currBal = topUpParams[0]
            topUpVal = blitValInt
            ref.update({"topupBalance":topUpVal})
            newBal = currBal + topUpVal
            topUpRef.update({"balance":newBal})
            idleTimer = 11
            blitValInt = 0
            blitVal = "0"
            GPIO.output(relIn1, GPIO.HIGH)
            ser.close()
            GPIO.output(servoButB, GPIO.LOW)
            GPIO.output(servoButA, GPIO.HIGH)
            GPIO.output(extraButC, GPIO.HIGH)
            self.stateManager.setState('scene8')



        
        timer = topUpFont.render(idleTimerStr, 0, Red)
        self.display.blit(timer, (580,490))

class scene8:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):

        self.display.blit(topUpSuccess,(0,0))
        amountDisp = topUpFont.render(str(ref.child("topupBalance").get()), 0, Red)
        self.display.blit(amountDisp, (260,260))        

        global topEndTick

        topEndTick+=1

        if topEndTick > 180:      

            topEndTick = 0
            self.stateManager.setState('scene1')


        
class scene9:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):
        self.display.blit(coinTimeOut,(0,0))

        amountDisp = topUpFont.render(blitVal, 0, Red)
        self.display.blit(amountDisp, (240,480))        

        global topEndTick

        topEndTick+=1

        if topEndTick > 180:      

            topEndTick = 0
            self.stateManager.setState('scene1')


class scene10:
    def __init__(self, display, stateManager):
        self.display = display
        self.stateManager = stateManager

    def run(self, mouse, clicker):
        self.display.blit(maintenancePage,(0,0))
  



class stateManager:
    def __init__(self, currentScene):
        self.currentScene = currentScene
    
    def getState(self):
        return self.currentScene
    
    def setState(self, state):
        self.currentScene = state

if __name__ == '__main__':
    game = Game()
    game.run()