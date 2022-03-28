//MPU6050 (An IMU with accelerometer and gyroscope) For the Lightwave

//NOTE: The MPU6050 board is labeled "6Y-521", and takes VCC=5v

//This library comes from: https://github.com/adafruit/Adafruit_MPU6050
//Please note: There is one more adafruit library which I had to install to make Adafruit_MPU6050.h work, and it was installed from the Arduino IDE's library manager (like the other MPU6050 libraries were), but I forgot what it was called in-case you're compiling this on a new computer (not Ryan Burgert's 2013 Macbook Pro)
#include <Adafruit_MPU6050.h>//Arduino Library: Adafruit MPU6050 
#include <Adafruit_Sensor.h>//Arduino Library: "Adafruit Unified Sensor", find after searching "unified" See https://forum.arduino.cc/index.php?topic=471001.0
#include <Wire.h>

Adafruit_MPU6050 imu;//TODO: How do I choose the pins to use for this MPU? 

void setup_imu(void) 
{
  imu.begin();//This should return true, otherwise the IMU failed to start. I'll assume that it started correctly, because the Lightwave should have one hooked up.
  imu.setAccelerometerRange(MPU6050_RANGE_8_G     );//All options: MPU6050_RANGE_2_G    , MPU6050_RANGE_4_G    , MPU6050_RANGE_8_G     , MPU6050_RANGE_16_G     (Specifies +=range in Grams)
  imu.setGyroRange         (MPU6050_RANGE_1000_DEG);//All options: MPU6050_RANGE_250_DEG, MPU6050_RANGE_500_DEG, MPU6050_RANGE_1000_DEG, MPU6050_RANGE_2000_DEG (Specifies +=range in DEGrees per second)
  imu.setFilterBandwidth   (MPU6050_BAND_44_HZ    );//All options: MPU6050_BAND_260_HZ  , MPU6050_BAND_184_HZ  , MPU6050_BAND_94_HZ    , MPU6050_BAND_44_HZ, MPU6050_BAND_21_HZ, MPU6050_BAND_10_HZ, MPU6050_BAND_5_HZ (I'm not sure exactly what this specifies...)

  //To get readings:
  //  sensors_event_t a, g, temp;
  //  mpu.getEvent(&a, &g, &temp);
  //Then access results:
  //  a.acceleration.x
  //  a.acceleration.y
  //  a.acceleration.z
  //  g.gyro.x
  //  g.gyro.y
  //  g.gyro.z
}


