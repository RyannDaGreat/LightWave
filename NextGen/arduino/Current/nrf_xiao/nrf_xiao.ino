// SimpleRx - the slave or the receiver

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN   3
#define CSN_PIN  2

const byte thisSlaveAddress[5] = {'1','N','o','d','e'};

RF24 radio(CE_PIN, CSN_PIN);

//FOR TEENSY 4.1:
//#https://circuitpython-nrf24l01.readthedocs.io/en/latest/core_api/configure_api.html#circuitpython_nrf24l01.rf24.RF24.dynamic_payloads
//RF24.dynamic_payloads=False
//RF24.payload_length=32

//===========

void setup() {

//    Serial.begin(115200);
//    delay(500);
//    Serial.println("SimpleRx Starting A");
//    Serial.flush();
//    delay(500);
//    Serial.println("SimpleRx Starting B");
//    Serial.flush();
    //Documentation: https://maniacbug.github.io/RF24/classRF24.html
    radio.begin();
    radio.powerUp(); //Uses more power. Makes it more responsive.
    radio.setDataRate( RF24_1MBPS ); //RF24_1MBPS, RF24_250KBPS, RF24_2MBPS
//    radio.enableDynamicPayloads();
    radio.openReadingPipe(1, thisSlaveAddress);
    radio.setChannel(76); // Python default is 76. Lboard uses this. hich RF channel to communicate on, 0-127
    radio.setCRCLength(RF24_CRC_16); //In python, we have crc=2
    radio.disableCRC();
//    radio.setPayloadSize(32); // payload_length = 32
    radio.setAutoAck(false); //Default: true
    radio.startListening();
}

//=============

void loop() {
    getData();
    showData();
    delay(100);
    Serial.println(radio.testCarrier());
}

//==============

char dataReceived[32]; // this must match dataToSend in the TX
bool newData = false;

void getData() {
    if ( radio.available() ) {
        radio.read( &dataReceived, sizeof(dataReceived) );
        newData = true;
    }
}

void showData() {
    if (newData == true) {
        Serial.print("Data received ");
        Serial.println(dataReceived);
        newData = false;
    }
}
