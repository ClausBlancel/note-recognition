# Note Recognition for Music Score Creation (NRMSC)
A project for teensyduino, that create music score upon listening to a melody.

## Initialisation
To power up the Teensy, you need to connect it to a computer. Then connect a microphone to capture the sound of an instrument. Finally, run the Python script.

## How does it work in a global way?
The Teensy listens to the microphone and applies the Yin algorithm to find the fundamental frequency of the note being played. When it finds something, it sends it to the computer via the USB port. From the beginning, the Python script listens to the serial port and collects data from the Teensy.   

Then, in real time, it creates the score using a musicXML file, which can be displayed as a real score on the web (https://www.soundslice.com/musicxml-viewer/) or with an application such as MuseScore.

## What is the Yin algorithm?
Its purpose is to estimate the fundamental frequency of musical sounds. It has no upper limit on the frequency search range, is very fast and easy to use. It is based on autocorrelation.   

If the sound is loud and clear enough, we achieve perfect frequency recognition many times over, which means it can be reliable.

## Do we use something else?
In reality, we also use another tool : a peak detection. It sent a number between 0 and 1 which determine if we have a peak in amplitude in the signal.

## How does the Python script works?
So the script collects the frequency and the value of the peak. Each time it detects a peak, it creates an eighth note in the musicXML file at the good frequency. Then it waits either for the duration of a eighth note to see if another one is played immediately after it, or for a peak to appear. Finally, it updates the musicXML file by dividing the time between these peaks by the tempo (which represents the number of quarter notes per minute): it represents the duration of the note, so it types (eighth / quarter / half / whole note).   

We test a lot of different algorithms, but this one is the most reliable.

## Limits
Our measurements show that the time between two data samples sent by the Teensy is 70 ms. This seems good, but in reality, if we set the tempo to 120 (that's 120 beats per minute), an eighth note can be played every 250 ms, which means we have 3 data samples to determine if it's a new note being played or if it's the same note.   

In practice, that's not enough to be realiable. So we decided, after testing, that the whole song would be played at a tempo of 60 to have enough data to process.   

Furthermore, if everything is set up correctly, it works incredibly well, but if the sound is not loud enough, it is possible to capture nothing or something very, very bad (we cannot recognise the melody at all).

## What we can do next?
For now we are able to recognise a melody played by a solo instrument. If we find a way to get more samples from the Teensy, it may be a good idea to play the music at the right tempo and let the script find the right tempo, weave and frame. Why not also find the right instrument?   

Then we can try to recognise accords played by one instrument, and try to capture multiple melodies from multiple instruments.   

For the piano, it can also be a matter of putting a note in the treble or bass clef depending on its frequency.
