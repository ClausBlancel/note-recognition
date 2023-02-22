from math import log2
from pymusicxml import *
import serial
import io

with serial.Serial('/dev/ttyS1', 19200, timeout=1) as ser:
    line = ser.readline()
    print(line)

finished = False
listNote = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
score = Score(title="Read from the Teensy", composer="Teensy")

part = Part("Piano")
score.append(part)
measure = Measure()
measureReinit = Measure()


def convertFreqToNote(freq):
    noteInFloat = 69 + 12 * log2(float(freq) / 440)
    noteInInt = round(noteInFloat)
    noteInLetter = listNote[noteInInt % 12]
    octaveOfTheNote = str(int(noteInInt / 12) - 1)
    return noteInLetter + octaveOfTheNote


while not finished:
    userInput = input("Enter a note: ")
    if userInput == "Stop":
        finished = True
    else:
        note = Note(pitch=convertFreqToNote(userInput), duration=1)
        measure.append(note)
    part.append(measure)
    score.export_to_file("test.xml")
    part.__delitem__(0)

