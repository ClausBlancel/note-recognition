#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

//---------------------------------------------------------------------------------------
AudioAnalyzeNoteFrequency	notefreq;
AudioAnalyzeRMS					 rms;
AudioAnalyzePeak				peak;
AudioInputI2S					i2s1;
AudioMixer4					   mixer;
AudioControlSGTL5000		sgtl5000;
//---------------------------------------------------------------------------------------
AudioConnection patchCord0(i2s1, 0, mixer, 0);
AudioConnection patchCord1(mixer, 0, notefreq, 0);
AudioConnection patchCord2(i2s1, 0, rms, 0);
AudioConnection patchCord3(i2s1, 0, peak, 0);
//---------------------------------------------------------------------------------------

void setup() {
	Serial.begin(9600);
	AudioMemory(30);

	notefreq.begin(.15);

	sgtl5000.enable();
	sgtl5000.volume(0.5);
	sgtl5000.inputSelect(AUDIO_INPUT_MIC);
	sgtl5000.micGain(36);
}

void loop() {
	if (notefreq.available() and rms.available() and peak.available()) {
		float note = notefreq.read();
		float prob = notefreq.probability();
		float amp = rms.read();
		float highest = peak.read();
		Serial.printf("%3.2f,%.2f,%.2f,%.2f\n", note, prob, amp, highest);
	}
}