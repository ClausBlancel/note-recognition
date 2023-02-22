#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>


// GUItool: begin automatically generated code
AudioInputI2S            i2s1;
AudioOutputI2S            i2s2;
// AudioSynthKarplusStrong  string1;
// AudioAnalyzeNoteFrequency notefreq1;
AudioAnalyzeRMS rms1;
AudioConnection          patchCord1(i2s1, 0, rms1, 0);
AudioConnection          patchCord2(i2s1, 0, i2s2, 0);
AudioControlSGTL5000     sgtl5000_1;     //xy=690,481
// GUItool: end automatically generated code


void setup() {
	Serial.begin(9600);
	AudioMemory(8);
	sgtl5000_1.enable();
	sgtl5000_1.volume(0.5);
	sgtl5000_1.inputSelect(AUDIO_INPUT_MIC);
	sgtl5000_1.micGain(36);
	// notefreq1.begin(.15);
}

void loop() {
	// string1.noteOn(300, 1.0);
	if (rms1.available()) {
		float value = rms1.read();
		Serial.printf("Value : %f\n", value);
	}
	/* if (notefreq1.available()) {
		float note = notefreq1.read();
		float prob = notefreq1.probability();
		Serial.printf("Note: %3.2f | Probability: %.2f\n", note, prob);
	} */
	delay(1000);
}