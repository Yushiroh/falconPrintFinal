import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

while True:

    # coinVal = ser.read(2)
    # print(coinVal.decode("utf-8"))

    RF = ser.read(8)
    print(RF.decode("utf-8"))


