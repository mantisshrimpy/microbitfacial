"""
Flash this onto microbit

listens on the USB serial connection for a single character sent by
pc_smile_detector.py
    s=  happy face
    f= show a sad face
    n= (or nothing detected)
"""

from microbit import *

uart.init(baudrate=115200)

current = "N"

happy = Image.HAPPY
sad = Image.SAD
neutral = Image(
    "00000:"
    "00000:"
    "99999:"
    "00000:"
    "00000"
)

display.show(neutral)

while True:
    if uart.any():
        data = uart.read(1)
        if data:
            char = chr(data[0])
            if char in ("S", "F", "N") and char != current:
                current = char
                if char == "S":
                    display.show(happy)
                elif char == "F":
                    display.show(sad)
                else:
                    display.show(neutral)
    sleep(50)
