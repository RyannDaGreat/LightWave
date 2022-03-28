#include <CapacitiveSensor.h>
CapacitiveSensor capSensor = CapacitiveSensor(8,12); //[[USE LIKE THIS: cs_4_8.capacitiveSensor(500) --> int]] 1M resistor between pins 8 (or 9, 9 is the same with the current wiring...its just the opposite side of the pot) & 12, pin 12 is sensor pin, add a wire and or foil.
//The following two int parameters were decided after running Serial.println(capSensor.capacitiveSensor(500)); in loop for a while and looking at the numbers
int capOffThreshold=50;
int capOnThreshold=250;
//It appeared that usually the value would be in the single digit range unless touched, in which case it spikes to about 1000
//I'm going to set a modest threshold of 50 to 200. 
//The dual-threshold algorithm is equivalent to a tether with a single threshold, except it's faster and easier to write.
inline int getCapSensorValue()
{
  return capSensor.capacitiveSensor(500);
}
bool _capSensorValueMem; 
inline bool getCapSensorTouched()
{
  int x=getCapSensorValue();
  if(x>capOnThreshold)
  {
    _capSensorValueMem=true;
  }
  else if(x<capOffThreshold)
  {
    _capSensorValueMem=false;
  }
  return _capSensorValueMem;
}
//FOR TESTING THIS MODULE ALONE:
//void setup()
//{
//  Serial.begin(9600);
//}
//void loop()
//{
//  Serial.println(getCapSensorTouched());
//}

