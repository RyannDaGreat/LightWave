#include <ArduinoJson.h>

//SCRAPPED. I'm pretty sure this code is perfectly fine, but for some reason it doesn't seem to be compatiable with ArduinoJSON. Maybe I made a mistake somewhere?!?! (I spent a few hours coding this...) I don't know why this doesn't work; but I'm going to do away with it in favor of a more hacky solution (just temporarily inserting a null terminator).
//struct CharBufferReader
//{
// 
//    // This is a custom reader class to let ArduinoJson parse MsgPack into a JsonDocument
//    // It's meant to work with my Escaper class's buffer
//    // Documentation: https://arduinojson.org/v6/api/msgpack/deserializemsgpack/
//
//    char * src_buffer  ;
//    size_t src_length  ;
//    size_t cursor_index;
//    CharBufferReader(char*src_buffer,size_t src_length)
//    {
//        this->src_buffer  =src_buffer;
//        this->src_length  =src_length;
//        this->cursor_index=0         ;
//    }
//
//    int read()
//    {
//        Serial.print("CALREAD");Serial.print(cursor_index);Serial.print(src_length);Serial.println();
//        // Reads one byte, or returns -1
//        if(cursor_index>=src_length)
//        {
//            return -1;
//        }
//        return (unsigned char)src_buffer[cursor_index++];//Added (unsigned char): Did it fail because sometimes the char it returned would be -1 (becuase in arduino characters are signed and could be -1 when not erroring, the 'byte' type in arduino is an unsigned char, and the documentation said it had to return a byte or -1)
//    }
//
//    size_t readBytes(char*dst_buffer,size_t read_length)
//    {
//      Serial.print("CALREAD BY ");Serial.print(read_length);Serial.println();
//      
//        // Reads several bytes, returns the number of bytes read.
//        if(cursor_index>=src_length)
//        {
//            return 0;//We've allready read the whole buffer, so we return 0 because we've read 0 bytes
//        }
//        const int unread_length=src_length-cursor_index;
//        if(read_length>unread_length)
//        {
//            read_length=unread_length;
//        }
//        for(int i=0;i<read_length;i++)
//        {
//            dst_buffer[i]=src_buffer[cursor_index++];
//        }
//        return read_length;
//    }
//};

bool try_parse_msgpack(char*buffer,size_t length,JsonDocument &doc)
{ 
    //Returns 0 for success, and 1 for failure (see https://stackoverflow.com/questions/9549342/should-i-return-0-or-1-for-successful-function/9549375)
    //See ArduinoJSON deserializeMsgPack   Documentation: https://arduinojson.org/v6/api/msgpack/deserializemsgpack/
    //See ArduinoJSON DeserializationError Documentation: https://arduinojson.org/v6/api/misc/deserializationerror/
//    CharBufferReader reader=CharBufferReader(*buffer,length);
    char temp=buffer[length];//Temporarily create a null terminator right after the buffer (for ArduinoJson to parse it. This might seem unsafe (we might go out of bounds), but we'll restore this before we return from this funtion...)
    buffer[length]=0;//Add a null terminator if none 
    boolean errored=deserializeMsgPack(doc,buffer)!=DeserializationError::Ok;//True if error, false otherwise
    buffer[length]=temp;//...and we restore the byte
    return errored;
}

