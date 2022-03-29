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
  middle_left. begin( 4, 5);
  middle_right.begin( 2, 3);
  bottom_left. begin( 8, 9);
  bottom_right.begin( 6, 7);
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

//ImuDelayLine imu_0;
//ImuDelayLine imu_1;
//ImuDelayLine imu_2;
//ImuDelayLine imu_3;
//ImuDelayLine imu_4;
//ImuDelayLine imu_5;
ImuDelayLine imu_6;

void loop() 
{  
                                             //imu_0.update();
  top_left_reading     = top_left    .read();//imu_1.update();
  top_right_reading    = top_right   .read();//imu_2.update();
  middle_left_reading  = middle_left .read();//imu_3.update();
  middle_right_reading = middle_right.read();//imu_4.update();
  bottom_left_reading  = bottom_left .read();//imu_5.update();
  bottom_right_reading = bottom_right.read();imu_6.update();

  top_left_reading    =top_left_median    (top_left_reading    );
  top_right_reading   =top_right_median   (top_right_reading   );
  middle_left_reading =middle_left_median (middle_left_reading );
  middle_right_reading=middle_right_median(middle_right_reading);
  bottom_left_reading =bottom_left_median (bottom_left_reading );
  bottom_right_reading=bottom_right_median(bottom_right_reading);
  
                                                       //imu_0.print();Serial.print(',');
  Serial.print(top_left_reading    );Serial.print(',');//imu_1.print();Serial.print(',');
  Serial.print(top_right_reading   );Serial.print(',');//imu_2.print();Serial.print(',');
  Serial.print(middle_left_reading );Serial.print(',');//imu_3.print();Serial.print(',');
  Serial.print(middle_right_reading);Serial.print(',');//imu_4.print();Serial.print(',');
  Serial.print(bottom_left_reading );Serial.print(',');//imu_5.print();Serial.print(',');
  Serial.print(bottom_right_reading);Serial.print(',');imu_6.print();//Serial.print(',');

  Serial.println();//There will be one trailing comma
}
