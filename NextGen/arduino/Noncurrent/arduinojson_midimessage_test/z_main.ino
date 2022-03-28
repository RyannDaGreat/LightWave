StaticJsonDocument<500> json_doc ;
Unescaper         <500> unescaper;

//Here's how I benchmarked this:
//from serial import Serial
//s=Serial(input_select_serial_device_id(),baudrate=115200)
//def escapeify(message:bytes):
//    return message.replace(b'\\',b'\\\\').replace(b'\n',b'\\n')
//def talk(*message,wait=.02):
//    message=packb(message)
//    message=escapeify(message)
//    message=bytes(message)
//    message+=b'\n'
//    fansi_print(len(message),'cyan','bold')
//    assert isinstance(message,bytes)
//    
//    fansi_print('Sending:'+str(list(message)),'red')
//    s.write(message)
//    
//    sleep(wait)
//    out= s.read_all()
//    print(out.decode())
//THEN, I spammed: talk({'gigglk234oe':[2,3,4],'midi':[[1,.2,3],[4,.35],[6,234,1.40],[23,23]]*1},wait=.005)
//Findings: The type checks I have in here make an inperceptible differnce in timing (I can't see a difference of even 1ms)


void handle_midi_message(JsonArray &midi_message)
{
    Serial.print("\tMidi Message: ");
    for(int i:midi_message)
    {
        Serial.print("\t\t");
        Serial.print(i);
        Serial.println();
    }
//    serializeJson(midi_message,Serial);
//    Serial.println();
}

void handle_midi_messages(JsonArray &midi_messages)
{
    for(JsonVariant element : midi_messages)
    {
        if(element.is<JsonArray>())
        {
            JsonArray midi_message=element.as<JsonArray>();
            handle_midi_message(midi_message);
        }
    }
}

void json_doc_handler()
{
    //Returns true if errored
    //Gets called each time unescaper_handler succesfully parses a msgpack buffer into json_doc
    //The name of this function refers to the global variable json_doc
    Serial.println("RECEIVED JSON");//serializeJson(json_doc, Serial);Serial.println();//It's not serializing right...

    if(not json_doc.size()>=1)
        return;//This breaks the schema I've planned for my data.

    Serial.println("Good 1");

    JsonVariant data=json_doc[0];
    
    if(not data.is<JsonObject>())
        return;//This breaks the schema I've planned for my data.

    Serial.println("Good 2");

    if(data.containsKey("midi"))
    {
        Serial.println("Good 3");
        JsonVariant midi_data=data["midi"];
        if(midi_data.is<JsonArray>())
        {
            Serial.println("Good 4");
            Serial.println("Detected MIDI messages!");
            JsonArray midi_messages=midi_data.as<JsonArray>();
            handle_midi_messages(midi_messages);
        }
    }
}

void unescaper_handler(char*buffer,unsigned int length)
{
    Serial.println("RECEIVED MESSAGE");//About 2ms
    bool failed_to_parse_msgpack=try_parse_msgpack(buffer,length,json_doc);
    if(not failed_to_parse_msgpack)
    {
        json_doc_handler();
    }
    else
    {
        Serial.println("FAILED TO PARSE MSGPACK DOCUMENT");
    }
}

void loop() 
{
    unescaper.feed(serial_read,serial_available,unescaper_handler);
}

void setup() 
{
    Serial.begin(115200);
    while (!Serial) continue;
}

