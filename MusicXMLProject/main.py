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
lastFreqGivenByTeensy = 0
lastNote = 0
lastAmpli = 1
tempo = 80
timeBetweenNote = (60 / tempo) - 0.05
d = 1


def convertFreqToNote(freq):
    noteInFloat = 69 + 12 * log2(float(freq) / 440)
    noteInInt = round(noteInFloat)
    noteInLetter = listNote[noteInInt % 12]
    octaveOfTheNote = str(int(noteInInt / 12) - 1)
    return noteInLetter + octaveOfTheNote


def createNote(d, freq):
    note = Note(pitch=convertFreqToNote(freq), duration=d)
    measure.append(note)
    part.append(measure)
    score.export_to_file("test.xml")
    part.__delitem__(0)

while True:
    with serial.Serial('COM3', 9600, timeout=1) as ser:
        line = ser.readline()
        # print("line =", line)
        
    
    if line != b'': 
        line = str(line)[2:]
        line = line[:len(line)-3]
        freq, proba, ampli = line.split(",")

        freq = float(freq)
        proba = float(proba)
        ampli = float(ampli)
        
        now = time.time()

        print(line)
        if proba > 0.85 and ampli > 0.09:
            lastFreqNoteRecognized = freq

        if abs(now - lastNote) > timeBetweenNote and proba > 0.85 and ampli > 0.09:
            print("----------",line)

            # On détecte une nouvelle note jouée (donc on créée celle d'avant)
            if ampli > lastAmpli: 
                createNote(d, lastFreqNoteRecognized)
                print("Note créée")
                d = 1
                
            # On détecte pas une nouvelle note jouée
            elif ampli <= lastAmpli: 
                lastFreqNoteRecognized = freq
                d = 2 
                print("Note blanche reconnue")


            lastNote = time.time()
        
        lastAmpli = ampli    
        lastFreqGivenByTeensy = freq
