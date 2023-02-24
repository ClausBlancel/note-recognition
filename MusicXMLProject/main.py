from math import log2
from pymusicxml import *
import serial
import io
import time
import xml.etree.ElementTree as ET

listNote = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
score = Score(title="Read from the Teensy", composer="Teensy")

part = Part("Piano")
score.append(part)
score.export_to_file("test.xml")


tree = ET.parse('test.xml')
root = tree.getroot()

part = ET.Element("part")
part.set("id", "P1")
measure = ET.Element("measure")
measure.set("number", "1")
part.append(measure)
root.append(part)


tempo = 80
timeBetweenNote = (60 / tempo) 
firstNote = True
tabFreq = []
tabAmpli = []
tabProba = []
partition = []
thisNote = 0
lastAmpli = 0
blanche = False


def convertFreqToNote(freq):
    noteInFloat = 69 + 12 * log2(float(freq) / 440)
    noteInInt = round(noteInFloat)
    noteInLetter = listNote[noteInInt % 12]
    octaveOfTheNote = str(int(noteInInt / 12) - 1)
    return noteInLetter + octaveOfTheNote


def createNote(d, freq):
    # note = Note(pitch=convertFreqToNote(freq), duration=d)
    # measure.append(note)
    # part.append(measure)
    # score.write_file("test.xml")
    # part.__delitem__(0)
   
    noteStr = convertFreqToNote(freq)

    new_note = ET.Element("note")
    pitch = ET.Element("pitch")
    step = ET.Element("step")
    step.text = noteStr[0:1]
    octave = ET.Element("octave")
    octave.text = noteStr[-1]
    pitch.append(step)
    pitch.append(octave)
    duration = ET.Element("duration")
    duration.text = str(d)  # valeur de duration de la nouvelle note
    type = ET.Element("type")
    type.text = "quarter"
    new_note.append(pitch)
    new_note.append(duration)
    new_note.append(type)
    measure = root.findall("./part/measure")
    lastMeasure = measure[-1]
    lastMeasure.append(new_note)

    tree.write("test.xml")


def modifierNote(d):
    notes = root.findall("./part/measure/note")
    if notes:
        last_note = notes[-1]
        last_duration = last_note.find("duration")
        last_duration.text = "2"  # la nouvelle valeur de duration
        last_type = last_note.find("type")
        last_type.text = "half"
        # Enregistrer les modifications dans le fichier XML
        tree.write("test.xml")
    else:
        print("Le fichier ne contient pas de notes.")

while True:
    with serial.Serial('COM3', 9600, timeout=1) as ser:
        line = ser.readline()
        # print("line =", line)
        
    
    if line != b'': 
        line = str(line)[2:]
        line = line[:len(line)-3]
        print(line)
        freq, proba, ampli, peak = line.split(",")

        freq = float(freq)
        proba = float(proba)
        ampli = float(ampli)
        peak = float(peak)

        tabFreq.append(freq)
        tabProba.append(proba)    
        tabAmpli.append(ampli)


        # if len(tabFreq) > 4 and tabAmpli[-2] > tabAmpli[-3] and tabAmpli[-2] > tabAmpli[-1] and tabAmpli[-2] - tabAmpli[-3] >= 0.05:
        #     if not firstNote:
        #         duration = round(abs(thisNote - time.time() / timeBetweenNote))
        #         print(abs(thisNote - time.time() / timeBetweenNote))
        #         print(duration)

        #         createNote(duration, tabFreq[-1])
                

        #     thisNote = time.time()
        #     firstNote = False
            
        if abs(thisNote - time.time()) > timeBetweenNote:
            if proba > 0.9 and peak > 0.8:
                createNote(1, freq)
                print("---noire---", freq)
                thisNote = time.time()
                lastAmpli = ampli
                blanche = False
                
            elif not blanche and ampli < lastAmpli:
                modifierNote(2)  # modifier ici
                print("---blanche---", freq)
                blanche = True
                thisNote = time.time()
