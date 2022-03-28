//unsigned int color(int red,int green, int blue)
//{
//  return strip.Color(red,green,blue);
//}
//
int numberOfNotes=7;
int colors[7][3]=
{
  {128,128,128},
  {255,0,0},
  {255,255,0},
  {0,255,0},
  {0,255,255},
  {0,0,255},
  {255,0,255}
};
//
int lowIntensityDenominator=6;//Means to divide by this int. High intensity is 1
//
int fingerNumLed;
void setFingerNumLed(int n)
{
  if(n>=0)
    fingerNumLed=n;
}
//
int numLedPerNote=3;
void setNumLedPerNote(int n)
{
  if(n>0)
    numLedPerNote=n;
}
//
inline int _numLedToNote(int numled)//Notes are in modulo
{
  return (numled/numLedPerNote)%numberOfNotes;
}
//
void setBlankCanvas()
{
  for (int i = 0; i < strip.numPixels(); i++)
  {
    strip.setPixelColor(i,0);
  }
}
//
void updateUniformNumledMode()
{
  for (int i = 0; i < strip.numPixels(); i++)
  {
    int n=_numLedToNote(i);
    int fingn=_numLedToNote(fingerNumLed);//finger note
    int denominator=(n==fingn)?1:lowIntensityDenominator;
    if(i%numLedPerNote!=numLedPerNote/2&&!(n==fingn))
    {
      denominator+=400;
    }
    strip.setPixelColor(i,
                          strip.Color(
//                                  colors[0][n]/denominator,
//                                  colors[1][n]/denominator,
//                                  colors[2][n]/denominator
                                  colors[n][0]/denominator,
                                  colors[n][1]/denominator,
                                  colors[n][2]/denominator
                               )
                        );
      if(i==fingerNumLed)
      {
        strip.setPixelColor(i,strip.Color(255,255,255));
      }
//    if(i%12==maxl%12)
//    {
//      strip.setPixelColor(i, strip.Color(255,255,255));
//    }
  }
}

