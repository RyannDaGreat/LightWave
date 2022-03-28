StaticJsonDocument<500> json_doc ;
Unescaper         <500> unescaper;

inline char serial_read()
{
    return Serial.read();
}

inline unsigned int serial_available()
{
    return Serial.available();
}

void json_doc_handler()
{
    //Gets called each time unescaper_handler succesfully parses a msgpack buffer into json_doc
    //The name of this function refers to the global variable json_doc
    Serial.println("RECEIVED JSON:");serializeJson(json_doc, Serial);//It's not serializing right...
    if(json_doc.containsKey("giggle"))
    {
        Serial.println("HAHAHA HA AHHA AHAHAHAH HA AHAHAHHA        HA");
    }
    else
    {
        Serial.println("Not funny.");
    }
}

void unescaper_handler(char*buffer,unsigned int length)
{
    Serial.print("GOT MESSAGE: [");
    for(int i=0;i<length;i++)
    {
      Serial.print((int)(unsigned char)buffer[i]);
      Serial.print(',');
    }
    Serial.println("]");

    bool failed_to_parse_msgpack=try_parse_msgpack(buffer,length,json_doc);
    if(not failed_to_parse_msgpack)
    {
        json_doc_handler();
    }
    else
    {
        Serial.println("FAILED TO PKKARSE MSGPACK DOCUMENT");
    }
}

void loop() 
{
    unescaper.feed(serial_read,serial_available,unescaper_handler);
}

void setup() 
{
    Serial.begin(115200);
//
    while (!Serial) continue;
//
//    
    Serial.println("STARTED, IMA DO A THING");
//
////    char*buffer="\x93\x01\x02\x03";
//
////    char*buffer="\x9a\xcd\x01\xc1\xcd\x01Wp\xd1\xff,\xcd\x02)\xd1\xfe\xea\xcd\x02\x99\xcd\x01\x00\xcd\x02\x9f\xcd\x03e";
////    char*buffer="\x9a\xcd\x03Q\xcd\x01\xfd\xcd\x01{\xd1\xfd1\xd1\xfe\xd8\xd1\xfd\x92\xd1\xfd\x00\xd1\xfe\xb3\xd1\xfcS\xd1\xff\x15";
////char*buffer="\x9a\xcd\x03I\x15\xcd\x03!\xd1\xfe \xd1\xff\x00\xd1\xfe\xf6\xd1\xff \xd1\xfd\x04\xd1\xfc\xef\\";//Should be: [841, 21, 801, -480, -256, -266, -224, -764, -785, 92]
////char*buffer="\x9a\xcd\x03\x00\xd1\xfcu\xd0\xba\xcd\x03\x8d\xd1\xfdx\xd1\xfd\xc0\xd1\xfe\x1b\xcd\x03\xa1\xd1\xffP\xd1\xfd\x88";//Should be: [768, -907, -70, 909, -648, -576, -485, 929, -176, -632]
////char*buffer="\x9a\xd1\xfcR\xcd\x01\xcd\xcc\xd8\xd1\xfc\xf1\xcd\x03\x02\xcd\x01\x00\xcd\x01\x94\xcd\x02\xf4\xcd\x01o\xd1\xfc\x8b";//Should be: [-942, 461, 216, -783, 770, 256, 404, 756, 367, -885]
//char*buffer="\x9a\xd1\xfd\xa5\xd1\xfc\xf2\xcd\x02\xed\xcd\x01=N\xcd\x01\xba\xcd\x02\xf4\xcd\x02e\xd1\xfe\xfe\xd1\xfe\x00";//Should be: [-603, -782, 749, 317, 78, 442, 756, 613, -258, -512]
//Serial.println("PRINTING CHARS IN BUFFER
////
////    yield();
//        json_doc.clear();
//    json_doc["PONIES"]=123;
//    serializeJsonPretty(json_doc, Serial);
//    serializeJson(json_doc, Serial);
//
//    Serial.println("AND THEN");
////        bool failed_to_parse_msgpack=try_parse_msgpack(buffer,4,json_doc);
//deserializeMsgPack(json_doc,buffer);
//        serializeJsonPretty(json_doc, Serial);
//          Serial.println("AND ALSO");
//    serializeJson(json_doc, Serial);
//      Serial.println("SO YEAH");
//    return;
}

