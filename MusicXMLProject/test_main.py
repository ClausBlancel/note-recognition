from math import log2
from pymusicxml import *
import serial
import io
import time
import xml.etree.ElementTree as ET
import threading

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


tempo = 120
timeBetweenCroche = (60 / tempo) / 2
firstTime = True
lastFreq = 0


def convertFreqToNote(freq):
    noteInFloat = 69 + 12 * log2(float(freq) / 440)
    noteInInt = round(noteInFloat)
    noteInLetter = listNote[noteInInt % 12]
    octaveOfTheNote = str(int(noteInInt / 12) - 1)
    return noteInLetter + octaveOfTheNote


def createNote(d, freq):   
    noteStr = convertFreqToNote(freq)
    print(noteStr, freq)
    print("---croche---", freq)

    new_note = ET.Element("note")
    pitch = ET.Element("pitch")
    step = ET.Element("step")
    alter = ET.Element("alter")
    octave = ET.Element("octave")
    step.text = noteStr[0]
    octave.text = noteStr[-1]
    if len(noteStr) == 3:
        if noteStr[1] == '#':
            alter.text = "1"
        else:
            alter.text = "-1"
    else:
        alter.text = "0"
    pitch.append(step)
    pitch.append(alter)
    pitch.append(octave)
    duration = ET.Element("duration")
    duration.text = str(d)  # valeur de duration de la nouvelle note
    type = ET.Element("type")
    type.text = "eighth"
    new_note.append(pitch)
    new_note.append(duration)
    new_note.append(type)
    measure = root.findall("./part/measure")
    lastMeasure = measure[-1]
    lastMeasure.append(new_note)

    tree.write("test.xml")


def modifierNote(d, freq):
    notes = root.findall("./part/measure/note")
    if notes:
        last_note = notes[-1]
        last_duration = last_note.find("duration")
        last_duration.text = str(d)  # la nouvelle valeur de duration
        last_type = last_note.find("type")
        listNote = {1: "eighth", 2 : "quarter", 4 : "half", 8 : "whole"}
        print("-----", listNote[d], "-----", freq)
        last_type.text = listNote[d]
        # Enregistrer les modifications dans le fichier XML
        tree.write("test.xml")
    else:
        print("Le fichier ne contient pas de notes.")

try:
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
                   
            # print(timeBetweenNote, abs(thisNote - absoluteTimeNoteBefore))  
            if peak > 0.9:     
                if not firstTime:
                    timeBetweenLastNoteDetected = absoluteTimeNoteBefore - time.time() 
                    print("timeBetweenLastNoteDetected = ", abs(timeBetweenLastNoteDetected))
                    nbTemps = round(abs(timeBetweenLastNoteDetected / timeBetweenCroche))
                    if nbTemps in [2,4,8]:
                        absoluteTimeNoteBefore = time.time()
                        procModifyNote = threading.Thread(target=modifierNote,args=(int(nbTemps), lastFreq, )) 
                        procModifyNote.start()
                    if nbTemps in [1,2,4,8]:
                        absoluteTimeNoteBefore = time.time()
                        procCreateNote = threading.Thread(target=createNote, args=(0.5, freq,))
                        procCreateNote.start()
                        lastFreq = freq
                else:
                    lastFreq = freq
                    absoluteTimeNoteBefore = time.time()
                    firstTime = False
                    procCreateNote = threading.Thread(target=createNote, args=(0.5, freq,))
                    procCreateNote.start() 
                
                    
except:
    timeBetweenLastNoteDetected = absoluteTimeNoteBefore - time.time() 
    nbTemps = round(abs(timeBetweenLastNoteDetected / timeBetweenCroche))
    procModifyNote = threading.Thread(target=modifierNote,args=(nbTemps, lastFreq, ))
    