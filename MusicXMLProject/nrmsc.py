import os
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


tempo = 60
timeBetweenCroche = (60 / tempo) / 2
firstTime = True
firstPeak = True
lastFreq = 0
global listRhythm
listRhythm = {1: "eighth", 2: "quarter", 4: "half", 8: "whole"}

# listAmpli = []


def convertFreqToNote(freq):
    noteInFloat = 69 + 12 * log2(float(freq) / 440)
    noteInInt = round(noteInFloat)
    noteInLetter = listNote[noteInInt % 12]
    octaveOfTheNote = str(int(noteInInt / 12) - 1)
    return noteInLetter + octaveOfTheNote


def createNote(d, freq):
    noteStr = convertFreqToNote(freq)
    # print(noteStr, freq)
    print("------ Nouvelle note :", noteStr, "------")

    new_note = ET.Element("note")
    pitch = ET.Element("pitch")
    step = ET.Element("step")
    alter = ET.Element("alter")
    octave = ET.Element("octave")
    thisNote = listNote.index(noteStr[0])
    thisOctave = int(noteStr[-1])
    if thisNote < 5 and thisOctave <= 3:
        thisOctave = thisOctave + 1

    step.text = noteStr[0]
    octave.text = str(thisOctave)

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

    nbMeasure = 1
    measure = root.findall("./part/measure")
    lastMeasure = measure[-1]
    # Create a new measure if the last one is full
    if len(lastMeasure) == 4:
        measure = ET.Element("measure")
        measure.set("number", str(nbMeasure))
        part.append(measure)
        nbMeasure += 1
        measure = root.findall("./part/measure")
        lastMeasure = measure[-1]
        lastMeasure.append(new_note)
    else:
        lastMeasure = measure[-1]
        lastMeasure.append(new_note)

    # print(len(lastMeasure))
    tree.write("test.xml")


def modifierNote(d, freq):
    notes = root.findall("./part/measure/note")
    if notes:
        last_note = notes[-1]
        last_duration = last_note.find("duration")
        last_duration.text = str(d)  # la nouvelle valeur de duration
        last_type = last_note.find("type")
        # listRhythm = {1: "eighth", 2 : "quarter", 4 : "half", 8 : "whole"}
        # print("-----", listRhythm[d], "-----", freq)
        last_type.text = listRhythm[d]
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
            # print(line)
            freq, proba, ampli, peak = line.split(",")

            freq = float(freq)
            proba = float(proba)
            ampli = float(ampli)
            peak = float(peak)

            # listAmpli.append(ampli)

            # print(timeBetweenNote, abs(thisNote - absoluteTimeNoteBefore))
            if peak == 1:
                if not firstPeak:
                    if not firstTime:
                        timeBetweenLastNoteDetected = absoluteTimeNoteBefore - time.time()
                        # print("timeBetweenLastNoteDetected = ", abs(timeBetweenLastNoteDetected), "/", timeBetweenCroche)
                        nbTemps = round(abs(timeBetweenLastNoteDetected / timeBetweenCroche))
                        if nbTemps in [2,4,8]:
                            print("Longueur de la note : ", listRhythm[nbTemps])
                            absoluteTimeNoteBefore = time.time()
                            procModifyNote = threading.Thread(target=modifierNote,args=(int(nbTemps), lastFreq, ))
                            procModifyNote.start()
                        if nbTemps in [2,4,8] or abs(abs(timeBetweenLastNoteDetected) - timeBetweenCroche) < 0.06:
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
                firstPeak = False
            else:
                firstPeak = True
                    
except:
    timeBetweenLastNoteDetected = absoluteTimeNoteBefore - time.time()
    procModifyNote = threading.Thread(target=modifierNote,args=(4, lastFreq, ))
    procModifyNote.start()

    # Open MuseScore with the test.xml file
    os.startfile("test.xml")
