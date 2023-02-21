#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

// GUItool: begin automatically generated code
AudioInputI2S            i2s2;           //xy=640,278
AudioAnalyzeNoteFrequency notefreq1;      //xy=888,347
AudioConnection          patchCord1(i2s2, 0, notefreq1, 0);
AudioControlSGTL5000     sgtl5000_1;     //xy=690,481
// GUItool: end automatically generated code


void setup() {
	Serial.begin(9600);
	AudioMemory(8);
	sgtl5000_1.enable();
	sgtl5000_1.volume(0.5);
	sgtl5000_1.inputSelect(AUDIO_INPUT_MIC);
	sgtl5000_1.micGain(36);
	delay(1000);
	notefreq1.begin(.15);
}

void loop() {
	if (notefreq1.available()) {
		float note = notefreq1.read();
		float prob = notefreq1.probability();
		Serial.printf("Note: %3.2f | Probability: %.2f\n", note, prob);
	}
	delay(1000);
}