//Nothing here. See Z_Main for the code that run; it has to come after HX711

//Some useful information (copied from the Notes app):
//    
//    ESP32_DEVKIT_C_V4 PINS:
//    (All data gathered experimentally with an LED)
//    0   0
//    1   TX (Don't use as GPIO or else serial will lock up without an error)
//    2   2
//    3   RX (Don't use as GPIO or else serial will lock up without an error)
//    4   4
//    5   5 SS? https://learn.sparkfun.com/tutorials/esp32-thing-hookup-guide/using-the-arduino-addon
//    6   ?? (Don't use as GPIO or else "Guru Meditation Error: Core  0 panic'ed (IllegalInstruction)" and ESP32 will crash)
//    7   ?? (Don't use as GPIO or else "Guru Meditation Error: Core  0 panic'ed (IllegalInstruction)" and ESP32 will crash)
//    8   ?? (Don't use as GPIO or else "Guru Meditation Error: Core  0 panic'ed (IllegalInstruction)" and ESP32 will crash)
//    9   D2
//    10  D3
//    11  ?? (Don't use as GPIO or else "Guru Meditation Error: Core  0 panic'ed (IllegalInstruction)" and ESP32 will crash)
//    12  12
//    13  13
//    14  14
//    15  15
//    16  16
//    17  17
//    18  18  (SCLK aka SCK)? https://learn.sparkfun.com/tutorials/esp32-thing-hookup-guide/using-the-arduino-addon
//    19  19  MISO? https://learn.sparkfun.com/tutorials/esp32-thing-hookup-guide/using-the-arduino-addon
//    20  ?? ValueError: invalid pin (Couldn't even get GPIO to turn on in the first place)
//    21  21
//    22  22  
//    23  23  MOSI? https://learn.sparkfun.com/tutorials/esp32-thing-hookup-guide/using-the-arduino-addon
//    24  ?? ValueError: invalid pin (Couldn't even get GPIO to turn on in the first place)
//    25  25
//    26  26
//    27  27
//    28  ?? ValueError: invalid pin (Couldn't even get GPIO to turn on in the first place)
//    29  ?? ValueError: invalid pin (Couldn't even get GPIO to turn on in the first place)?? ValueError: invalid pin (Couldn't even get GPIO to turn on in the first place)
//    30  ?? ValueError: invalid pin (Couldn't even get GPIO to turn on in the first place)
//    31  ?? ValueError: invalid pin (Couldn't even get GPIO to turn on in the first place)
//    32  32
//    33  33
//    34  ? ValueError: pin can only be input
//    35  ? ValueError: pin can only be input
//    36  ? ValueError: pin can only be input
//    37  ? ValueError: pin can only be input
//    38  ? ValueError: pin can only be input
//    39  ? ValueError: pin can only be input
//    (Pins 40 and above are all invalid)
