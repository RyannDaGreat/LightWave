#include <ArduinoJson.h>

bool try_parse_msgpack(char*buffer,size_t length,JsonDocument &doc)
{ 
    //Returns 0 for success, and 1 for failure (see https://stackoverflow.com/questions/9549342/should-i-return-0-or-1-for-successful-function/9549375)
    //See ArduinoJSON deserializeMsgPack   Documentation: https://arduinojson.org/v6/api/msgpack/deserializemsgpack/
    //See ArduinoJSON DeserializationError Documentation: https://arduinojson.org/v6/api/misc/deserializationerror/
    char temp=buffer[length];//Temporarily create a null terminator right after the buffer (for ArduinoJson to parse it. This might seem unsafe (we might go out of bounds), but we'll restore this before we return from this funtion...)
    buffer[length]=0;//Add a null terminator if none 
    boolean errored=deserializeMsgPack(doc,buffer)!=DeserializationError::Ok;//True if error, false otherwise
    buffer[length]=temp;//...and we restore the byte
    return errored;
}

