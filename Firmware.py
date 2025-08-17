// ---- Libraries (install via Arduino Library Manager) ----
// Adafruit NeoPixel by Adafruit
// SparkFun_APDS-9960 by SparkFun (for APDS-9960)
// If using PAJ7620 instead, swap library & gesture handling.



Adafruit_NeoPixel strip(NUM_LEDS, PIN_LED_DATA, NEO_GRB + NEO_KHZ800);
SparkFun_APDS9960 apds = SparkFun_APDS9960();

uint8_t brightness = 80;      // 0..255
uint16_t hue = 0;             // 0..65535 if using HSV helper
uint8_t mode = 0;             // 0: solid color, 1: rainbow, 2: vu-ish pulse

void setSolidHSV(uint16_t h, uint8_t s=255, uint8_t v=255) {
  // quick HSV→RGB approximation using NeoPixel ColorHSV
  uint32_t color = strip.gamma32(strip.ColorHSV(h, s, v));
  for (int i=0; i<NUM_LEDS; i++) strip.setPixelColor(i, color);
  strip.show();
}

void rainbow() {
  static uint16_t j=0;
  for (uint16_t i=0; i<NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.gamma32(strip.ColorHSV((i*65536/NUM_LEDS)+j)));
  }
  strip.show();
  j += 256; // speed
}

void pulseSolid() {
  static int t=0;
  uint8_t v = (sin(t*0.1)*0.5 + 0.5) * brightness;
  uint32_t color = strip.gamma32(strip.ColorHSV(hue, 255, v));
  for (int i=0; i<NUM_LEDS; i++) strip.setPixelColor(i, color);
  strip.show();
  t++;
}

void nextMode() { mode = (mode + 1) % 3; }

void setup() {
  pinMode(MODE_BTN, INPUT_PULLUP);
  Wire.begin(I2C_SDA, I2C_SCL);
  strip.begin();
  strip.setBrightness(brightness);
  strip.show();

  if (apds.init()) {
    apds.enableGestureSensor(true);
  }

  setSolidHSV(hue);
}

void handleGestures() {
  if (apds.isGestureAvailable()) {
    switch (apds.readGesture()) {
      case DIR_LEFT:   if (hue >= 4096) hue -= 4096; else hue = 65535; setSolidHSV(hue, 255, brightness); break;
      case DIR_RIGHT:  hue = (hue + 4096) % 65536; setSolidHSV(hue, 255, brightness); break;
      case DIR_UP:     if (brightness < 245) brightness += 10; strip.setBrightness(brightness); break;
      case DIR_DOWN:   if (brightness > 10) brightness -= 10; strip.setBrightness(brightness); break;
      case DIR_NEAR:
      case DIR_FAR:    nextMode(); break;
    }
  }
}

void loop() {
  // mode button as alternative to gesture near/far
  static uint32_t lastBtn = 0;
  if (millis() - lastBtn > 250 && digitalRead(MODE_BTN) == LOW) {
    nextMode();
    lastBtn = millis();
  }

  handleGestures();

  switch (mode) {
    case 0: setSolidHSV(hue, 255, brightness); delay(15); break;
    case 1: strip.setBrightness(brightness); rainbow(); delay(15); break;
    case 2: strip.setBrightness(brightness); pulseSolid(); delay(15); break;
  }
}
