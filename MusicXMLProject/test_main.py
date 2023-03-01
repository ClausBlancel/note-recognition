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


tempo = 80
timeBetweenNote = (60 / tempo) / 2
firstNote = True
firstTime = True
thisNote = 0
lastAmpli = 0
nbCroches = 0
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
        listNote = {0.5 : "eighth", 1 : "quarter", 2 : "half", 4 : "whole"}
        print("-----", listNote[d], "-----", freq)
        last_type.text = listNote[d]
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


        now = time.time()        
        print(timeBetweenNote, abs(thisNote - now))  
        if abs(thisNote - now) > timeBetweenNote:
            if (peak > 0.9 or abs(lastFreq - freq) > 5) and proba > 0.9:
                procCreateNote = threading.Thread(target=createNote, args=(0.5, freq,))
                procCreateNote.start()
                if not firstTime:
                    thisNote += timeBetweenNote
                else:
                    thisNote = now
                    firstTime = False
                # createNote(0.5, freq)
                lastAmpli = ampli
                # print("Last Ampli = ", lastAmpli)
                nbCroches = 1
                thisNote = now
                lastFreq = freq
                
            else:
                if nbCroches == 1: 
                    procModifyNote = threading.Thread(target=modifierNote,args=(1, freq, )) 
                    procModifyNote.start()
                    # modifierNote(1, freq)
                    lastAmpli = ampli
                    
                    
                elif nbCroches == 3:
                    procModifyNote = threading.Thread(target=modifierNote,args=(2, freq,)) 
                    procModifyNote.start()
                    # modifierNote(2, freq)
                    lastAmpli = ampli
                    
                elif nbCroches == 7:
                    procModifyNote = threading.Thread(target=modifierNote,args=(4, freq,)) 
                    procModifyNote.start()  
                    # modifierNote(4, freq)
                    lastAmpli = ampli
                    
                nbCroches += 1
                print(nbCroches)
                thisNote += timeBetweenNote
                lastFreq = freq
                
