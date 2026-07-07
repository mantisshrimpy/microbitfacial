"""
smile detector 

ueses  webcam + openCV to detect a face and whether its smiling,
then sends a single character over USB serial to a micro:bit, which
lights up a happy or sad face

for set up on
    pip install opencv python pyserial

use
    1 flash microbit_display.py onto  micrbit first 
    2. plug the microbit into usb
    3. run : python pc_smile_detector.py
    4 q to exit the window 

"""

import time

import cv2
import serial
import serial.tools.list_ports
#set up for serial

def find_microbit_port():

    for port in serial.tools.list_ports.comports():
        desc = (port.description or "").lower()
        if "mbed" in desc or "micro" in desc or "microbit" in desc:
            return port.device
    return None


PORT = find_microbit_port()
if PORT is None:
    print("Could not auto-detect micro:bit. Edit PORT in this script manually.")
    PORT = "COM7"  # change if autodetect fail, had issues with this 

BAUD = 115200

try:
    mb = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(1)  # connection settling 
    print(f"Connected to micro:bit on {PORT}")


except serial.SerialException as e:
    print(f"Could not open {PORT}: {e}")
    print(" video preview will still run, it just wont control the microbit :(")
    mb = None


def send_state(state):
    """send a single character to the microbit S smile, F sad,"""
    if mb is not None:
        mb.write(state.encode())



#uses opencv built in haar cascade

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("could not open webcam")

last_state = None

# tweak this if detection feels too happy (raise) or not happy enough (lower)
SMILE_MIN_NEIGHBORS = 25

while True:
    ok, frame = cap.read()
    if not ok:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(100, 100))

    state = "N"  #if no face detected

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]

        smiles = smile_cascade.detectMultiScale(
            roi_gray, scaleFactor=1.7, minNeighbors=SMILE_MIN_NEIGHBORS, minSize=(25, 15)
        )

        state = "S" if len(smiles) > 0 else "F"
        label = "Smiling :)" if state == "S" else "Not smiling :("
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        break  # only react to the first face found

    if state != last_state:
        send_state(state)
        last_state = state

    cv2.imshow("Face test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
if mb is not None:
    mb.close()
