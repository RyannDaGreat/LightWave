//This section implements a rolling median with three elements, to prevent spikes when the sensor reads incorrectly (spike handling can be done on the Nano, instead of the ESP32, as it's the nano's fault for the wrong reading in the first place)

long middleOfThree(long a, long b, long c) 
{ 
    //This function runs in constant time. Right now computational efficiency is NOT a bottleneck; the HX711's are.
    //https://www.geeksforgeeks.org/middle-of-three-using-minimum-comparisons/
    // Compare each three number to find middle  
    // number. Enter only if a > b 
    if (a > b)  
    { 
        if (b > c) 
            return b; 
        else if (a > c) 
            return c; 
        else
            return a; 
    } 
    else 
    { 
        // Decided a is not greater than b. 
        if (a > c) 
            return a; 
        else if (b > c) 
            return c; 
        else
            return b; 
    } 
} 

long ranking(long value,long array[],long length)
{
  //Returns the number of elements in array that are less than or equal to value
  long out=0;
  for(int i=0;i<length;i++)
  {
    if(array[i]>value)
    {
      out++;
    }
  }
  return out;
}

long median(long array[],long length)
{
  long out=0;
  int minRank=length+100;
  for(int i=0;i<length;i++)
  {
    long value=array[i];
    long rank=ranking(value,array,length);
    if(rank>=length/2)
    {
      if(rank<minRank)
      {
        minRank=rank;
        out=value;
      }
    }
  }
  return out;
}


struct RollingTripletMedian
{
  //A small rolling median with three elements
  long triplet[3];
  int index=0;
  //Overloading the call operator
  long operator()(long input)
  { 
    index++;
    if(index>=3)
    {
      index=0;
    }
    triplet[index]=input;
//    return input;
//    return triplet[index];
    return middleOfThree(triplet[0],triplet[1],triplet[2]);
  }
};

const int eleven=5;  //As it turns out, a median window of 5 is enough to block all spikes, but 3 is not.
struct RollingElevenMedian
{
  //THIS BIG MESS IS to prevent spikes in our measurements without introducing 3 samples of latency. It's not perfect.
  //This can probably be done well on the ESP, but it's simple to test it on the nano...
  //A small rolling median with three elements
  long triplet[eleven];
  int index=0;
  //Overloading the call operator
  long operator()(long input)
  { 
//    return input;//for comparison with no filter. uncomment to enable
    index++;
    if(index>=eleven)
    {
      index=0;
    }
    triplet[index]=input;
//    return input;
//    return triplet[index];
    long med= median(triplet,eleven);
    
    //Take the newest measurement if it's within a threshold of the median (allow vibrato and faster response times by about 2/80 seconds)
    long threshold=100000;//I got this number from looking at the size of the spikes on the plot. Note that this threshold isn't in grams, because right now I have a mix of 1kg and 10kg load cells, and i suspect it's either an electrical or bit shift error (so the spikes shuldnt be scaled down etc)
//    if(abs(med-input)<threshold)
//    {
//      return input;
//    }

//
    threshold=75000;long middle=triplet[(index+eleven/2)%eleven];input=middle;//(optional line might comment this line out) reduce jerkyness at the cost of small latency that reduces the response from aronud 1/80 sec to 1/20 sec...

    float alpha=min(1,fabs(med-input)/threshold);//More alpha -> more median. A softer version of the harsher if() block commented out above...
    return long(alpha*med+(1-alpha)*input);

    return med;
  }
};

const int delayLength=eleven/2+1;
struct FloatDelayLine
{
  float history[delayLength];
  int index=0;
  float operator()(float input)
  {
    history[index]=input;
    index++;
    if(index>=delayLength)
    {
      index=0;
    }
    return history[index];//It hasn't been assigned yet, so this is the last element in the list...
  }
};

struct ImuDelayLine
{
  FloatDelayLine accel_x_delayline;
  FloatDelayLine accel_y_delayline;
  FloatDelayLine accel_z_delayline;
  FloatDelayLine gyro_x_delayline;
  FloatDelayLine gyro_y_delayline;
  FloatDelayLine gyro_z_delayline;
  
  float accel_x;
  float accel_y;
  float accel_z;
  float gyro_x;
  float gyro_y;
  float gyro_z;

  void update()
  {
    sensors_event_t a, g, temp;
    imu.getEvent(&a, &g, &temp);
      
    accel_x=accel_x_delayline(a.acceleration.x);
    accel_y=accel_y_delayline(a.acceleration.y);
    accel_z=accel_z_delayline(a.acceleration.z);
    
    gyro_x =gyro_x_delayline(g.gyro.x);
    gyro_y =gyro_y_delayline(g.gyro.y);
    gyro_z =gyro_z_delayline(g.gyro.z);
  }

  void print()
  {
    //NOTE: Serial.print(val, 4);  // print floating point variable showing four digits after decimal point
    
    Serial.print(accel_x,4);Serial.print(',');
    Serial.print(accel_y,4);Serial.print(',');
    Serial.print(accel_z,4);Serial.print(',');
    
    Serial.print(gyro_x ,4);Serial.print(',');
    Serial.print(gyro_y ,4);Serial.print(',');
    Serial.print(gyro_z ,4);
  }
};

