/**
 *
 * HX711 library for Arduino
 * https://github.com/bogde/HX711
 *
 * MIT License
 * (c) 2018 Bogdan Necula
 *
**/
#ifndef HX711_h
#define HX711_h

#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

class HX711
{
  private:
    byte PD_SCK;  // Power Down and Serial Clock Input Pin
    byte DOUT;    // Serial Data Output Pin
    byte GAIN;    // amplification factor
    long OFFSET = 0;  // used for tare weight
    float SCALE = 1;  // used to return weight in grams, kg, ounces, whatever

  public:

    HX711();

    virtual ~HX711();

    // Initialize library with data output pin, clock input pin and gain factor.
    // Channel selection is made by passing the appropriate gain:
    // - With a gain factor of 64 or 128, channel A is selected
    // - With a gain factor of 32, channel B is selected
    // The library default is "128" (Channel A).
    void begin(byte dout, byte pd_sck, byte gain = 128);

    // Check if HX711 is ready
    // from the datasheet: When output data is not ready for retrieval, digital output pin DOUT is high. Serial clock
    // input PD_SCK should be low. When DOUT goes to low, it indicates data is ready for retrieval.
    bool is_ready();

    // Wait for the HX711 to become ready
    void wait_ready(unsigned long delay_ms = 0);
    bool wait_ready_retry(int retries = 3, unsigned long delay_ms = 0);
    bool wait_ready_timeout(unsigned long timeout = 1000, unsigned long delay_ms = 0);

    // set the gain factor; takes effect only after a call to read()
    // channel A can be set for a 128 or 64 gain; channel B has a fixed 32 gain
    // depending on the parameter, the channel is also set to either A or B
    void set_gain(byte gain = 128);

    // waits for the chip to be ready and returns a reading
    long read();

    // returns an average reading; times = how many times to read
    long read_average(byte times = 10);

    // returns (read_average() - OFFSET), that is the current value without the tare weight; times = how many readings to do
    double get_value(byte times = 1);

    // returns get_value() divided by SCALE, that is the raw value divided by a value obtained via calibration
    // times = how many readings to do
    float get_units(byte times = 1);

    // set the OFFSET value for tare weight; times = how many times to read the tare value
    void tare(byte times = 10);

    // set the SCALE value; this value is used to convert the raw data to "human readable" data (measure units)
    void set_scale(float scale = 1.f);

    // get the current SCALE
    float get_scale();

    // set OFFSET, the value that's subtracted from the actual reading (tare weight)
    void set_offset(long offset = 0);

    // get the current OFFSET
    long get_offset();

    // puts the chip into power down mode
    void power_down();

    // wakes up the chip after power down mode
    void power_up();

    long ryread();
};

#endif /* HX711_h */

/**
 *
 * HX711 library for Arduino
 * https://github.com/bogde/HX711
 *
 * MIT License
 * (c) 2018 Bogdan Necula
 *
**/
//#include <Arduino.h>
//#include "HX711.h"

// TEENSYDUINO has a port of Dean Camera's ATOMIC_BLOCK macros for AVR to ARM Cortex M3.
#define HAS_ATOMIC_BLOCK (defined(ARDUINO_ARCH_AVR) || defined(TEENSYDUINO))

// Whether we are running on either the ESP8266 or the ESP32.
#define ARCH_ESPRESSIF (defined(ARDUINO_ARCH_ESP8266) || defined(ARDUINO_ARCH_ESP32))

// Whether we are actually running on FreeRTOS.
#define IS_FREE_RTOS defined(ARDUINO_ARCH_ESP32)

// Define macro designating whether we're running on a reasonable
// fast CPU and so should slow down sampling from GPIO.
#define FAST_CPU \
    ( \
    ARCH_ESPRESSIF || \
    defined(ARDUINO_ARCH_SAM)     || defined(ARDUINO_ARCH_SAMD) || \
    defined(ARDUINO_ARCH_STM32)   || defined(TEENSYDUINO) \
    )

#if HAS_ATOMIC_BLOCK
// Acquire AVR-specific ATOMIC_BLOCK(ATOMIC_RESTORESTATE) macro.
#include <util/atomic.h>
#endif

#if FAST_CPU
// Make shiftIn() be aware of clockspeed for
// faster CPUs like ESP32, Teensy 3.x and friends.
// See also:
// - https://github.com/bogde/HX711/issues/75
// - https://github.com/arduino/Arduino/issues/6561
// - https://community.hiveeyes.org/t/using-bogdans-canonical-hx711-library-on-the-esp32/539
uint8_t shiftInSlow(uint8_t dataPin, uint8_t clockPin, uint8_t bitOrder) {
    uint8_t value = 0;
    uint8_t i;

    for(i = 0; i < 8; ++i) {
        digitalWrite(clockPin, HIGH);
        delayMicroseconds(1);
        if(bitOrder == LSBFIRST)
            value |= digitalRead(dataPin) << i;
        else
            value |= digitalRead(dataPin) << (7 - i);
        digitalWrite(clockPin, LOW);
        delayMicroseconds(1);
    }
    return value;
}
#define SHIFTIN_WITH_SPEED_SUPPORT(data,clock,order) shiftInSlow(data,clock,order)
#else
#define SHIFTIN_WITH_SPEED_SUPPORT(data,clock,order) shiftIn(data,clock,order)
#endif


HX711::HX711() {
}

HX711::~HX711() {
}

void HX711::begin(byte dout, byte pd_sck, byte gain) {
  PD_SCK = pd_sck;
  DOUT = dout;

  pinMode(PD_SCK, OUTPUT);
  pinMode(DOUT, INPUT_PULLUP);

  set_gain(gain);
}

bool HX711::is_ready() {
  return digitalRead(DOUT) == LOW;
}

void HX711::set_gain(byte gain) {
  switch (gain) {
    case 128:   // channel A, gain factor 128
      GAIN = 1;
      break;
    case 64:    // channel A, gain factor 64
      GAIN = 3;
      break;
    case 32:    // channel B, gain factor 32
      GAIN = 2;
      break;
  }

  digitalWrite(PD_SCK, LOW);
  read();
}
long HX711::ryread() 
{
  while(digitalRead(DOUT));//Wait for the device to be ready
  int out=0;
  for(int i=0;i<24;i++)
  {
//    digitalWrite(PD_SCK,HIGH);
//    delayMicroseconds(1);
//    digitalWrite(PD_SCK,LOW);
//    delayMicroseconds(1);
    
    out=(out<<1)|digitalRead(DOUT);
  }

//  if(out>0x7fffff)
//  {
//    out-=0x1000000;
//  }

  return out;
}

long HX711::read() {

//  return ryread();
  // Wait for the chip to become ready.
  wait_ready();

  // Define structures for reading data into.
  unsigned long value = 0;
  uint8_t data[3] = { 0 };
  uint8_t filler = 0x00;

  // Protect the read sequence from system interrupts.  If an interrupt occurs during
  // the time the PD_SCK signal is high it will stretch the length of the clock pulse.
  // If the total pulse time exceeds 60 uSec this will cause the HX711 to enter
  // power down mode during the middle of the read sequence.  While the device will
  // wake up when PD_SCK goes low again, the reset starts a new conversion cycle which
  // forces DOUT high until that cycle is completed.
  //
  // The result is that all subsequent bits read by shiftIn() will read back as 1,
  // corrupting the value returned by read().  The ATOMIC_BLOCK macro disables
  // interrupts during the sequence and then restores the interrupt mask to its previous
  // state after the sequence completes, insuring that the entire read-and-gain-set
  // sequence is not interrupted.  The macro has a few minor advantages over bracketing
  // the sequence between `noInterrupts()` and `interrupts()` calls.
  #if HAS_ATOMIC_BLOCK
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {

  #elif IS_FREE_RTOS
  // Begin of critical section.
  // Critical sections are used as a valid protection method
  // against simultaneous access in vanilla FreeRTOS.
  // Disable the scheduler and call portDISABLE_INTERRUPTS. This prevents
  // context switches and servicing of ISRs during a critical section.
  portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
  portENTER_CRITICAL(&mux);

  #else
  // Disable interrupts.
  noInterrupts();
  #endif

  // Pulse the clock pin 24 times to read the data.
  data[2] = SHIFTIN_WITH_SPEED_SUPPORT(DOUT, PD_SCK, MSBFIRST);
  data[1] = SHIFTIN_WITH_SPEED_SUPPORT(DOUT, PD_SCK, MSBFIRST);
  data[0] = SHIFTIN_WITH_SPEED_SUPPORT(DOUT, PD_SCK, MSBFIRST);

  // Set the channel and the gain factor for the next reading using the clock pin.
  for (unsigned int i = 0; i < GAIN; i++) {
    digitalWrite(PD_SCK, HIGH);
    #if ARCH_ESPRESSIF
    delayMicroseconds(1);
    #endif
    digitalWrite(PD_SCK, LOW);
    #if ARCH_ESPRESSIF
    delayMicroseconds(1);
    #endif
  }

  #if IS_FREE_RTOS
  // End of critical section.
  portEXIT_CRITICAL(&mux);

  #elif HAS_ATOMIC_BLOCK
  }

  #else
  // Enable interrupts again.
  interrupts();
  #endif

  // Replicate the most significant bit to pad out a 32-bit signed integer
  if (data[2] & 0x80) {
    filler = 0xFF;
  } else {
    filler = 0x00;
  }

  // Construct a 32-bit signed integer
  value = ( static_cast<unsigned long>(filler) << 24
      | static_cast<unsigned long>(data[2]) << 16
      | static_cast<unsigned long>(data[1]) << 8
      | static_cast<unsigned long>(data[0]) );
  long out=static_cast<long>(value);
  if(out>0x7fffff)
  {
    out-=0x1000000;
  }
  return out;
}

void HX711::wait_ready(unsigned long delay_ms) {
  // Wait for the chip to become ready.
  // This is a blocking implementation and will
  // halt the sketch until a load cell is connected.
  while (!is_ready()) {
    // Probably will do no harm on AVR but will feed the Watchdog Timer (WDT) on ESP.
    // https://github.com/bogde/HX711/issues/73
    delay(delay_ms);
  }
}

bool HX711::wait_ready_retry(int retries, unsigned long delay_ms) {
  // Wait for the chip to become ready by
  // retrying for a specified amount of attempts.
  // https://github.com/bogde/HX711/issues/76
  int count = 0;
  while (count < retries) {
    if (is_ready()) {
      return true;
    }
    delay(delay_ms);
    count++;
  }
  return false;
}

bool HX711::wait_ready_timeout(unsigned long timeout, unsigned long delay_ms) {
  // Wait for the chip to become ready until timeout.
  // https://github.com/bogde/HX711/pull/96
  unsigned long millisStarted = millis();
  while (millis() - millisStarted < timeout) {
    if (is_ready()) {
      return true;
    }
    delay(delay_ms);
  }
  return false;
}

long HX711::read_average(byte times) {
  long sum = 0;
  for (byte i = 0; i < times; i++) {
    sum += read();
    // Probably will do no harm on AVR but will feed the Watchdog Timer (WDT) on ESP.
    // https://github.com/bogde/HX711/issues/73
    delay(0);
  }
  return sum / times;
}

double HX711::get_value(byte times) {
  return read_average(times) - OFFSET;
}

float HX711::get_units(byte times) {
  return get_value(times) / SCALE;
}

void HX711::tare(byte times) {
  double sum = read_average(times);
  set_offset(sum);
}

void HX711::set_scale(float scale) {
  SCALE = scale;
}

float HX711::get_scale() {
  return SCALE;
}

void HX711::set_offset(long offset) {
  OFFSET = offset;
}

long HX711::get_offset() {
  return OFFSET;
}

void HX711::power_down() {
  digitalWrite(PD_SCK, LOW);
  digitalWrite(PD_SCK, HIGH);
}

void HX711::power_up() {
  digitalWrite(PD_SCK, LOW);
}

