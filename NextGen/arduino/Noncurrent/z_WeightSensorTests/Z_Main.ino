HX711 top_left;
HX711 top_right;
HX711 middle_left;
HX711 middle_right;
HX711 bottom_left;
HX711 bottom_right;

//const int interrupt_pin=0;//DISABLED BECAUSE IT'S APPARENTLY IMPOSSIBLE. We're abusing the Nano's RX pin (which is pin 0) to send interrupts to the ESP32. The Nano never needs to read anything.

void setup() 
{
  Serial.begin(115200);
  //loadcell.begin(LOADCELL_DOUT_PIN (aka dt), LOADCELL_SCK_PIN (aka sck));
  top_left.    begin(11,10);
  top_right.   begin(12,13);
  middle_left. begin( 8, 9);
  middle_right.begin( 6, 7);
  bottom_left. begin( 4, 5);
  bottom_right.begin( 2, 3);

//  pinMode(interrupt_pin,OUTPUT);
}

void loop() 
{  
  long top_left_reading     = top_left    .read();
  long top_right_reading    = top_right   .read();
  long middle_left_reading  = middle_left .read();
  long middle_right_reading = middle_right.read();
  long bottom_left_reading  = bottom_left .read();
  long bottom_right_reading = bottom_right.read();
  
  Serial.print(top_left_reading    );
  Serial.print(",");
   
  Serial.print(top_right_reading   );
  Serial.print(",");
  
  Serial.print(middle_left_reading );
  Serial.print(",");
  
  Serial.print(middle_right_reading);
  Serial.print(",");
  
  Serial.print(bottom_left_reading );
  Serial.print(",");
  
  Serial.print(bottom_right_reading);
  Serial.println();

//  digitalWrite(interrupt_pin,HIGH);
//  delay(1);
//  digitalWrite(interrupt_pin,LOW);
}
