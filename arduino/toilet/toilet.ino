/* This example shows how to use continuous mode to take
range measurements with the VL53L0X. It is based on
vl53l0x_ContinuousRanging_Example.c from the VL53L0X API.

The range readings are in units of mm. */

#include <Wire.h>
#include <VL53L0X.h>
#include <Servo.h>

#define VB_DEBUG 1

int stall0_state_pin(A0);
int stall1_state_pin(A1);

/* VL530LX */
const byte VB0_XSHUT(4);
const byte VB1_XSHUT(5);
VL53L0X VB0;
VL53L0X VB1;
const uint16_t VB0_THOLD(145);
const uint16_t VB1_THOLD(120);
const uint16_t VB_DEADZONE(10); // +- 10


/* Servo */
Servo servo0;
Servo servo1;



/* Flushing */
const byte BUZZER0(2);
const byte UV0(3);
const byte BUZZER1(6);
const byte UV1(7);


/* loop() */
uint32_t prev_t(0);
const uint32_t LOOP_T(40);
const uint32_t FLUSH_T(4000);
const uint32_t FLUSH_DELAY(500);

bool stall0_state(false);
bool stall1_state(false);
bool stall0_state_prev(false);
bool stall1_state_prev(false);

int32_t flush0_timeout(0);
int32_t flush1_timeout(0);



/* VB_get_state() */
void VB_get_state();
void circular_array_add(uint8_t a[], uint8_t value, uint8_t &idx);
bool circular_array_avg(uint8_t a[]);

const uint8_t AVG_COUNT(10);
uint8_t stall0_state_record[AVG_COUNT]={};
uint8_t stall0_state_record_idx(0);
uint8_t stall1_state_record[AVG_COUNT]={};
uint8_t stall1_state_record_idx(0);



void setup(){
  Serial.begin(9600);


  pinMode(stall0_state_pin, OUTPUT);
  pinMode(stall1_state_pin, OUTPUT);

  
  /* Servo */
  servo0.attach(9);
  servo1.attach(10);


  
  /* Flushing */
  pinMode(BUZZER0, OUTPUT);
  pinMode(UV0, OUTPUT);
  pinMode(BUZZER1, OUTPUT);
  pinMode(UV1, OUTPUT);


  
  /* VL530LX */
  pinMode(VB0_XSHUT, OUTPUT);
  pinMode(VB1_XSHUT, OUTPUT);
  digitalWrite(VB1_XSHUT, LOW);
  
  Wire.begin();

  Serial.println("Hello");
  
  digitalWrite(VB0_XSHUT, HIGH);
  delay(2);
  VB0.setAddress(0x20);
  VB0.init();
  VB0.setTimeout(500);
  
  digitalWrite(VB1_XSHUT, HIGH);
  delay(2);
  VB1.setAddress(0x21);
  VB1.init();
  VB1.setTimeout(500);

  Serial.println("World");
  
  VB0.setMeasurementTimingBudget(20000);
  VB1.setMeasurementTimingBudget(20000);
  VB0.startContinuous();
  VB1.startContinuous();



}








void loop(){
  unsigned long now_t;
  do {
    now_t = millis();
  } while (now_t - prev_t < LOOP_T);

  VB_get_state();
  Serial.print(F("Stall 0: "));
  Serial.print(stall0_state);
  Serial.print(F("\tStall 1: "));
  Serial.println(stall1_state);


  if (stall0_state == false && stall0_state_prev == true && flush0_timeout <= 0){
    flush0_timeout = FLUSH_T;
  }
  if (stall1_state == false && stall1_state_prev == true && flush1_timeout <= 0){
    flush1_timeout = FLUSH_T;
  }

  /* action */
  if (stall0_state == true && flush0_timeout <= 0){
    servo0.write(185);
  } else {
    servo0.write(85);
  }
  if (stall1_state == true && flush1_timeout <= 0){
    servo1.write(170);
  } else {
    servo1.write(70);
  }
  
  if (flush0_timeout > 0 && flush0_timeout < FLUSH_T - FLUSH_DELAY){
    tone(BUZZER0, random(50, 500));
    digitalWrite(UV0, HIGH);
  } else {
    noTone(BUZZER0);
    digitalWrite(UV0, LOW);
  }
  if (flush1_timeout > 0 && flush1_timeout < FLUSH_T - FLUSH_DELAY){
    tone(BUZZER1, random(50, 500));
    digitalWrite(UV1, HIGH);
  } else {
    noTone(BUZZER1);
    digitalWrite(UV1, LOW);
  }



  /* Output */
  digitalWrite(stall0_state_pin, stall0_state == true ? HIGH : LOW );
  digitalWrite(stall1_state_pin, stall1_state == true ? HIGH : LOW );

  flush0_timeout -= now_t - prev_t;
  flush1_timeout -= now_t - prev_t;
  prev_t = now_t;
  stall0_state_prev = stall0_state;
  stall1_state_prev = stall1_state;
}



void circular_array_add(uint8_t a[], uint8_t value, uint8_t &idx){
  a[idx] = value;
  idx = (idx+1)%AVG_COUNT;
}

bool circular_array_avg(uint8_t a[]){
  uint8_t sum(0);
  for (int8_t i=0;i<AVG_COUNT;i++){
    sum += a[i];
  }
  return sum>=(AVG_COUNT/2);
}



void VB_get_state(){
  bool stall0_state_temp;
  bool stall1_state_temp;
  uint16_t VB0_range = VB0.readRangeContinuousMillimeters();
  uint16_t VB1_range = VB1.readRangeContinuousMillimeters();
  
  #if VB_DEBUG
  Serial.print(F("A\t"));
  Serial.print(VB0_range);
  if (VB0.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  
  Serial.print(F("\tB\t"));
  Serial.print(VB1_range);
  if (VB1.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  Serial.println();
  #endif

  if (!VB0.timeoutOccurred()) {
    if (stall0_state == true) {
      stall0_state_temp = VB0_range < VB0_THOLD + VB_DEADZONE;
    } else {
      stall0_state_temp = VB0_range < VB0_THOLD + VB_DEADZONE;
    }
  }
  if (!VB1.timeoutOccurred()) {
    if (stall1_state == true) {
      stall1_state_temp = VB1_range < VB1_THOLD + VB_DEADZONE;
    } else {
      stall1_state_temp = VB1_range < VB1_THOLD + VB_DEADZONE;
    }
  }

  

  circular_array_add(stall0_state_record, (uint8_t)stall0_state_temp, stall0_state_record_idx);
  stall0_state = circular_array_avg(stall0_state_record);
  circular_array_add(stall1_state_record, (uint8_t)stall1_state_temp, stall1_state_record_idx);
  stall1_state = circular_array_avg(stall1_state_record);




  
}

