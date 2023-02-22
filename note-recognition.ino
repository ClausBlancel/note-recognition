#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

#include "guitar_a2_note.h"

//---------------------------------------------------------------------------------------
AudioAnalyzeNoteFrequency notefreq;
AudioOutputAnalog         dac;
AudioPlayMemory           wav_note;
AudioMixer4               mixer;
//---------------------------------------------------------------------------------------
AudioConnection patchCord0(wav_note, 0, mixer, 0);
AudioConnection patchCord1(mixer, 0, notefreq, 0);
AudioConnection patchCord2(wav_note, 0, dac, 0);
//---------------------------------------------------------------------------------------

IntervalTimer playNoteTimer;

void playNote(void) {
	if (!wav_note.isPlaying()) {
		wav_note.play(guitar_a2_note);
	}
}

void setup() {
	Serial.begin(9600);
	AudioMemory(8);

	notefreq.begin(.15);

	playNoteTimer.priority(144);
	playNoteTimer.begin(playNote, 1000);
}

void loop() {
	if (notefreq.available()) {
		float note = notefreq.read();
		float prob = notefreq.probability();
		Serial.printf("Note: %3.2f | Probability: %.2f\n", note, prob);
	}
}