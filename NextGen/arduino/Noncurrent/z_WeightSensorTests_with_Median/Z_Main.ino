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
  setup_imu();
  //loadcell.begin(LOADCELL_DOUT_PIN (aka dt), LOADCELL_SCK_PIN (aka sck));
  top_left.    begin(11,10);
  top_right.   begin(12,13);
  middle_left. begin( 8, 9);
  middle_right.begin( 6, 7);
  bottom_left. begin( 4, 5);
  bottom_right.begin( 2, 3);

//  pinMode(interrupt_pin,OUTPUT);
}

RollingElevenMedian top_left_median    ;
RollingElevenMedian top_right_median   ;
RollingElevenMedian middle_left_median ;
RollingElevenMedian middle_right_median;
RollingElevenMedian bottom_left_median ;
RollingElevenMedian bottom_right_median;

long top_left_reading    ;
long top_right_reading   ;
long middle_left_reading ;
long middle_right_reading;
long bottom_left_reading ;
long bottom_right_reading;

ImuDelayLine imu_0,imu_1,imu_2,imu_3,imu_4,imu_5,imu_6,imu_7;

void loop() 
{  
//top_left    .power_down();
//top_right   .power_down();
//middle_left .power_down();
//middle_right.power_down();
//bottom_left .power_down();
//bottom_right.power_down();
//delay(1);
//top_left    .power_up();
//top_right   .power_up();
//middle_left .power_up();
//middle_right.power_up();
//bottom_left .power_up();
//bottom_right.power_up();
int n=0;
  delay(n);
  top_left_reading     = top_left    .read();
  delay(n);
  top_right_reading    = top_right   .read();
  delay(n);
  middle_left_reading  = middle_left .read();
  delay(n);
  middle_right_reading = middle_right.read();
  delay(n);
  bottom_left_reading  = bottom_left .read();
  delay(n);
  bottom_right_reading = bottom_right.read();
  delay(n);
////
//  Serial.print(top_left_reading    );
//  Serial.print(',');
//  Serial.print(top_right_reading   );
//  Serial.print(',');
//  Serial.print(middle_left_reading );
//  Serial.print(',');
//  Serial.print(middle_right_reading);
//  Serial.print(',');
//  Serial.print(bottom_left_reading );
//  Serial.print(',');
//  Serial.print(bottom_right_reading);
//  Serial.print(',');
////Serial.println();


  top_left_reading    =top_left_median    (top_left_reading    );
  top_right_reading   =top_right_median   (top_right_reading   );
  middle_left_reading =middle_left_median (middle_left_reading );
  middle_right_reading=middle_right_median(middle_right_reading);
  bottom_left_reading =bottom_left_median (bottom_left_reading );
  bottom_right_reading=bottom_right_median(bottom_right_reading);
//  
  Serial.print(top_left_reading    );
  Serial.print(',');
  Serial.print(top_right_reading   );
  Serial.print(',');
  Serial.print(middle_left_reading );
  Serial.print(',');
  Serial.print(middle_right_reading);
  Serial.print(',');
  Serial.print(bottom_left_reading );
  Serial.print(',');
  Serial.print(bottom_right_reading);
  Serial.println();

//  digitalWrite(interrupt_pin,HIGH);
//  delay(1);
//  digitalWrite(interrupt_pin,LOW);
}
