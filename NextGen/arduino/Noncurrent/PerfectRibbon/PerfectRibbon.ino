//Attempt to make a better ribbon reader for single touches...
//TODO: It glitches at the top and bottom of the ribbon. I suspect this is for the same reason averaging the two signals is technically innapropriate (though it does provide good smoothing). The noise, when near the top of the ribbon, is early all high or low (hypothesis(
//NOTE: The arduino's adc has this weird capacitor crap that makes the signal I send to the toggler all mushy, and low amplitude. Hopefuly the ADS1115 will fix this problem...

const int toggler=A1;
const int reader=A0;
float threshold=5;

void setup() 
{
  pinMode(toggler, OUTPUT);
  pinMode(reader, INPUT);
  Serial.begin(115200);
}

float previous;
float previous_average;
bool previous_gate;
bool state;

void loop()
{
  digitalWrite(toggler,state?HIGH:LOW);
  state=not state;
  
  float current=analogRead(reader);///1024.0;

  float average=(current+previous)/2;
  float gap=fabs(current-previous);
  previous=current;

//  Serial.print(current);
//  Serial.print(",");
//  Serial.print(average);
//  Serial.print(",");
//  Serial.print(gap);
//  Serial.println();

  //There is a solid theory behind this lag.
  //If mid-adc, the finger gets pressed or raised, even if the value is close enough to trigger a gate,
  //The value is still wrong, and should be skipped.
  bool gate=gap<threshold;
  if(gate and previous_gate)
  {
    Serial.print("0,1024,");
    Serial.print(previous_average);
    Serial.println();
  }
  previous_average=average;
  previous_gate=gate;

  //The one below doesn't work as well. My original theory says it shouldn't....but I can't quite make sense of why there are spikes...
//  bool gate=gap<threshold;
//  if(gate)
//  {
//    Serial.print("0,1024,");
//    Serial.print(average); 
//  }
//  previous_gate=gate;

}
