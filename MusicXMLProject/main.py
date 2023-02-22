from math import log2
from pymusicxml import *
import serial
import io
import time

listNote = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
score = Score(title="Read from the Teensy", composer="Teensy")

part = Part("Piano")
score.append(part)
measure = Measure()
measureReinit = Measure()
oldValue = 0
lastnote = 0
tempo = 80
timeBetweenNote = 60 / 80 


def convertFreqToNote(freq):
    noteInFloat = 69 + 12 * log2(float(freq) / 440)
    noteInInt = round(noteInFloat)
    noteInLetter = listNote[noteInInt % 12]
    octaveOfTheNote = str(int(noteInInt / 12) - 1)
    return noteInLetter + octaveOfTheNote

while True:
    with serial.Serial('COM3', 9600, timeout=1) as ser:
        line = ser.readline()
        # print("line =", line)
        
    
    if line != b'':
        i = 0
        value = ""
        line = str(line)[2:]
        line = line[:len(line)-3]
        value, proba, ampli = line.split(",")

        value = float(value)
        proba = float(proba)
        ampli = float(ampli)
        
        now = time.time()

        if (abs(value-oldValue) > 10 or abs(now - lastnote) > timeBetweenNote*2) and proba > 0.85 and ampli > 0.09:
            # print(value)
            print(line)
            note = Note(pitch=convertFreqToNote(value), duration=1)
            measure.append(note)
            part.append(measure)
            score.export_to_file("test.xml")
            part.__delitem__(0)
            i+=1
            lastnote = time.time()
        oldValue = value
