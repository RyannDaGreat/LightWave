StaticJsonDocument<500> json_doc ;
Unescaper         <500> unescaper;

void json_doc_handler()
{
    //Returns true if errored
    //Gets called each time unescaper_handler succesfully parses a msgpack buffer into json_doc
    //The name of this function refers to the global variable json_doc
    Serial.print("RECEIVED JSON:");serializeJson(json_doc, Serial);Serial.println();//It's not serializing right...

    if(not json_doc.size()>=1)
        return;//This breaks the schema I've planned for my data.

    JsonVariant data=json_doc[0];
    
    if(not data.is<JsonObject>())
        return;//This breaks the schema I've planned for my data.

    if(data.containsKey("MIDI") && data["MIDI"].is<JsonArray>)
    {
        Serial.println("Detected MIDI messages!");
        for(
    }
}

void unescaper_handler(char*buffer,unsigned int length)
{
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

