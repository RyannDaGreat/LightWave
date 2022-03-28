////MPU6050 (An IMU) For the Lightwave
//
////NOTE: The MPU6050 board is labeled "6Y-521", and takes VCC=5v
//
////This library comes from: https://github.com/adafruit/Adafruit_MPU6050
////Please note: There is one more adafruit library which I had to install to make Adafruit_MPU6050.h work, and it was installed from the Arduino IDE's library manager (like the other MPU6050 libraries were), but I forgot what it was called in-case you're compiling this on a new computer (not Ryan Burgert's 2013 Macbook Pro)
//#include <Adafruit_MPU6050.h>//Arduino Library: Adafruit MPU6050 
//#include <Adafruit_Sensor.h>//Arduino Library: "Adafruit Unified Sensor", find after searching "unified" See https://forum.arduino.cc/index.php?topic=471001.0
//#include <Wire.h>
//
//
//Adafruit_MPU6050 mpu;//TODO: How do I choose the pins to use for this MPU? 
//
//void setup(void) 
//{
//  Serial.begin(115200);
//
//  // Try to initialize!
//  if (!mpu.begin()) {
//    Serial.println("Failed to find MPU6050 chip");
//    while (1) {
//      delay(10);
//    }
//  }
//  Serial.println("MPU6050 Found!");
//
//  mpu.setAccelerometerRange(MPU6050_RANGE_8_G    );//All options: MPU6050_RANGE_2_G    , MPU6050_RANGE_4_G    , MPU6050_RANGE_8_G     , MPU6050_RANGE_16_G     (Specifies +=range in Grams)
//  mpu.setGyroRange         (MPU6050_RANGE_1000_DEG);//All options: MPU6050_RANGE_250_DEG, MPU6050_RANGE_500_DEG, MPU6050_RANGE_1000_DEG, MPU6050_RANGE_2000_DEG (Specifies +=range in DEGrees per second)
//  mpu.setFilterBandwidth   (MPU6050_BAND_44_HZ    );//All options: MPU6050_BAND_260_HZ  , MPU6050_BAND_184_HZ  , MPU6050_BAND_94_HZ    , MPU6050_BAND_44_HZ, MPU6050_BAND_21_HZ, MPU6050_BAND_10_HZ, MPU6050_BAND_5_HZ (I'm not sure exactly what this specifies...)
//}
//
//char mode='a';
//
//void loop() {
//
//  while(Serial.available()>0)
//  {
//    int new_mode=Serial.read();
//    switch(new_mode)
//    {
//      case 'b':
//        mode=(char)new_mode;
//        Serial.println("Set to mode 'b': gyroscope mode");
//        delay(1000);
//        break;
//      case 'a':
//        mode=(char)new_mode;
//        Serial.println("Set to mode 'a': accel mode");
//        delay(1000);
//        break;
//      default:
//        Serial.print("Invalid mode:");
//        Serial.print((char)new_mode);
//        Serial.println();
//        delay(1000);
//    }
//  }
//  /* Get new sensor events with the readings */
//  sensors_event_t a, g, temp;
//  mpu.getEvent(&a, &g, &temp);
//
//  if(mode=='a')
//  {
//    Serial.print(a.acceleration.x);
//    Serial.print(',');
//    Serial.print(a.acceleration.y);
//    Serial.print(',');
//    Serial.print(a.acceleration.z);
//    Serial.print(',');
//  }
//  else if(mode=='b')
//  {
//   Serial.print(g.gyro.x);
//   Serial.print(',');
//   Serial.print(g.gyro.y);
//   Serial.print(',');
//   Serial.print(g.gyro.z);
//   Serial.print(',');
//  }
//
//  Serial.println();
//
//
//  /* Print out the values */
//  // Serial.print("Acceleration X: ");
//  // Serial.print(a.acceleration.x);
//  // Serial.print(", Y: ");
//  // Serial.print(a.acceleration.y);
//  // Serial.print(", Z: ");
//  // Serial.print(a.acceleration.z);
//  // Serial.println(" m/s^2");
//
//  // Serial.print("Rotation X: ");
//  // Serial.print(g.gyro.x);
//  // Serial.print(", Y: ");
//  // Serial.print(g.gyro.y);
//  // Serial.print(", Z: ");
//  // Serial.print(g.gyro.z);
//  // Serial.println(" rad/s");
//
//  // Serial.print("Temperature: ");
//  // Serial.print(temp.temperature);
//  // Serial.println(" degC");
//
//  // Serial.println("");
//  // delay(500);
//}
