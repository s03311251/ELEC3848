#include <ESP8266WiFi.h>

const char* ssid     = "1915";
const char* password = "y5903112";
IPAddress host(192,168,0,188);
const int TCP_PORT = 38763;

const int TOILET_ID = 1;
const int STALL_NUM = 2;
bool stall_state[STALL_NUM] = {false, false};
unsigned long wait_t_buffer[100] = {};
unsigned int wait_t_buffer_idx = 0;



void add_wait_t_buffer(unsigned long t){
  wait_t_buffer[wait_t_buffer_idx] = t;
  wait_t_buffer_idx++;
}



void wifi_setup(){
  // We start by connecting to a WiFi network

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



void wifi_run(){
  Serial.print("connecting to ");
  Serial.println(host);
  
  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  if (!client.connect(host, TCP_PORT)) {
    Serial.println("connection failed");
    return;
  }

  // Send toilet information
  client.print(TOILET_ID);
  client.print(' ');
  client.print(STALL_NUM);
  
  for (int i=0;i<STALL_NUM;i++){
    client.print(' ');
    client.print(stall_state[i]);
  }
  while (wait_t_buffer_idx > 0){
    client.print(' ');
    client.print(wait_t_buffer[--wait_t_buffer_idx]);
  }
  client.println();

  // Read all the lines of the reply from server and print them to Serial
  while(client.available()){
    String line = client.readStringUntil('\r');
    Serial.print(line);
  }
  
  Serial.println("closing connection");
}



void setup() {
  Serial.begin(115200);
  delay(10);
  
  wifi_setup();
}

void loop() {
  delay(1000);

  add_wait_t_buffer(10);
  add_wait_t_buffer(20);
  wifi_run();
}

