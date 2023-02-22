from math import log2
from pymusicxml import *
import serial
import io

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

while True:
    with serial.Serial('COM3', 9600, timeout=1) as ser:
        line = ser.readline()
        # print("line =", line)
    
    if line != "b''":
        i = 0
        value = ""
        number = ["0","1","2","3","4","5","6","7","8","9","."]
        line = str(line)
        while line[i] not in number:
            i += 1
        while line[i] in number:
            value += line[i]
            i+=1

        value = float(value)
        print(value)

        note = Note(pitch=convertFreqToNote(value*(10**3)), duration=1)
        measure.append(note)
        part.append(measure)
        score.export_to_file("test.xml")
        part.__delitem__(0)
        i+=1
