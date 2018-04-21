void setup() {
  for (int i=2; i<=8; i+=2){
    pinMode(i, OUTPUT);
    pinMode(i+1, INPUT);
  }

  Serial.begin(9600);
}

void loop() {
  uint16_t reading_all = 0;
  for (int i=1; i<=4; i++){
    bool reading = digitalRead(i*2+1);
    reading_all |= !reading << (i-1);
    digitalWrite(i*2, reading);
  }

  uint8_t reading_array[2] = {};
  memcpy(reading_array, &reading_all, sizeof reading_all);
//  Serial.print(reading_array[0], HEX);
//  Serial.print(' ');
//  Serial.println(reading_array[1], HEX);
  Serial.write(reading_array[0]);
  Serial.write(reading_array[1]);

  delay(1000);
}
