#include <ESP8266WiFi.h>

//const char* ssid     = "AndroidAPFF";
//const char* password = "23838018806048";
const char* ssid     = "IDP2014";
const char* password = "12345678";

IPAddress host(192,168,0,191);
const int port = 38763;






const int stall0_state_pin(D0);
const int stall1_state_pin(D1);

bool stall0_state(false);
bool stall1_state(false);
bool stall0_state_prev(false);
bool stall1_state_prev(false);
uint32_t stall0_state_t(0);
uint32_t stall1_state_t(0);






const int cubicle_state_pin[4]{D5, D6, D7, D8};

bool cubicle_state[4]{false, false, false, false};
bool cubicle_state_prev[4]{false, false, false, false};
uint32_t cubicle_state_t[4]{0,0,0,0};
uint32_t cubicle_state_t_prev[4]{0,0,0,0};




uint32_t prev_t(0);

#define DEBUG 1

void setup() {
  Serial.begin(9600);
  
  pinMode(stall0_state_pin, INPUT);
  pinMode(stall1_state_pin, INPUT);
  for (int i=0;i<4;i++){
    pinMode(cubicle_state_pin[i], INPUT);
  }
  pinMode(A0, INPUT);
  uint32_t now_t = millis();
  stall0_state_t = now_t;
  stall1_state_t = now_t;
  for (int i=0;i<4;i++){
    cubicle_state_t_prev[i] = now_t;
  }

  /* WiFi */
  
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  
}




void loop() {
  uint8_t stall0_t_queue[100];
  uint8_t stall0_t_queue_idx(0);
  uint8_t stall1_t_queue[100];
  uint8_t stall1_t_queue_idx(0);
  uint32_t now_t = millis();

  /* toilet */
  stall0_state = digitalRead(stall0_state_pin) == HIGH ? true : false;
  stall1_state = digitalRead(stall1_state_pin) == HIGH ? true : false;

  if (stall0_state == true && stall0_state_prev == false){
    stall0_state_t = now_t;
  }
  else if (stall0_state == false && stall0_state_prev == true){
    stall0_t_queue[stall0_t_queue_idx] = (now_t - stall0_state_t) / 1000;
    stall0_t_queue_idx++;
  }
  
  if (stall1_state == true && stall1_state_prev == false){
    stall1_state_t = now_t;
  }
  else if (stall1_state == false && stall1_state_prev == true){
    stall1_t_queue[stall1_t_queue_idx] = (now_t - stall1_state_t) / 1000;
    stall1_t_queue_idx++;
  }


 /* cubicle */
 for (int i=0;i<4;i++){
  cubicle_state[i] = digitalRead(cubicle_state_pin[i]) == LOW ? true : false;
  
  if (cubicle_state[i] == true && cubicle_state_prev[i] == false){
    cubicle_state_t_prev[i] = now_t;
  }
  else if (cubicle_state[i] == false && cubicle_state_prev[i] == true){
    cubicle_state_t[i] = (now_t - cubicle_state_t_prev[i]) / 1000;
  }
 }
 
 #if DEBUG
  Serial.print(stall0_state);
  Serial.println(stall1_state);

  Serial.print(stall0_state_prev);
  Serial.println(stall1_state_prev);

  Serial.println("Stall 0: ");
  for (int i=0;i<stall0_t_queue_idx;i++){
    Serial.print(stall0_t_queue[stall0_t_queue_idx-1]);
    Serial.print(' ');
  }
  //stall0_t_queue_idx = 0;
  Serial.println();
  
  Serial.println("Stall 1: ");
  for (int i=0;i<stall1_t_queue_idx;i++){
    Serial.print(stall1_t_queue[stall1_t_queue_idx-1]);
    Serial.print(' ');
  }
  //stall1_t_queue_idx = 0;
  Serial.println();
  
  Serial.println("Cubicle: ");
  for (int i=0;i<4;i++){
    Serial.print(cubicle_state[i]);
    Serial.print(' ');
  }
  for (int i=0;i<4;i++){
    Serial.print(cubicle_state_t[i]);
    Serial.print(' ');
  }
  Serial.print("Battery: ");
  Serial.println(analogRead(A0));
  
 #endif



  /* Communication */
  Serial.print("connecting to ");
  Serial.println(host);
  
  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    return;
  }

  /* Toilet */
  client.print("1 2 ");
  client.print(stall0_state);
  client.print(' ');
  client.print(stall1_state);
  for (int i=0;i<stall0_t_queue_idx;i++){
    client.print(' ');
    client.print(stall0_t_queue[stall0_t_queue_idx-1]);
  }
  stall0_t_queue_idx = 0;
  for (int i=0;i<stall1_t_queue_idx;i++){
    client.print(' ');
    client.print(stall1_t_queue[stall1_t_queue_idx-1]);
  }
  stall1_t_queue_idx = 0;
  client.println();

  /* Cubicle */
  client.print("C");
  for (int i=0;i<4;i++){
    client.print(' ');
    client.print(cubicle_state[i]);
  }
  for (int i=0;i<4;i++){
    client.print(' ');
    client.print(cubicle_state_t[i]);
  }
  client.println();

  /* Battery */
  client.print("B");
  client.print(analogRead(A0));
  client.println();
  
  Serial.println("closing connection");























  prev_t = now_t;
  stall0_state_prev = stall0_state;
  stall1_state_prev = stall1_state;
   for (int i=0;i<4;i++){
    cubicle_state_prev[i] = cubicle_state[i];
    cubicle_state_t[i] = 0;
   }
  delay(1000);

}
