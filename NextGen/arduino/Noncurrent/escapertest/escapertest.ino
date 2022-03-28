//TO TRY THIS TEST: Try typing "the\nnasty\ngnome\nin\nneverland\nwhat\\is\\the\\meaning\\of\\life" into the monitor at baudrate 115200
//TODO: Make this for python. Writing is trivial (just search and replace), 
/*

Written by Ryan Burgert 2019

How to send separate messages over serial safely?

Goal: Send messages that can be checked, and if they're wrong, dump them.
Send arbitrary bytes (so just waiting for a '\n' doesn't cut it; I'd eventually like to use messagepack (which is a compressed version of JSON))

Escaping:
  Two Bytes:
    Delimiter byte
      This byte is never sent in any messages; when this byte is received it means 'end of message' like a null terminator.
    Escape byte
      There will be equal to or more of these in the final message than in the original
    Escape    Helper byte
      When this byte follows an escape byte, it's treated as the original escape character
      There will be equal to or more of these in the final message than in the orgiginal
    Delimiter Helper byte
      When this byte follows an escape byte, it's treated as the delimiter
      There will be equal to or more of these in the final message than in the orgiginal

    No two of these four bytes can be the same; that would break the algorithm
    The escape and delimiter bytes should be chosen to be chosen such that they appear least frequently in messages (the penalty is at most doubling the message size)
    The choice of byte for the delimiter helper and escape helper bytes shouldn't have any impact on performance or memory whatsoever (it's completely arbitrary. They just have to be unique, that's all.)

    How it works:
      Let's call the Delimiter Byte D,
                    the Escape byte E,
              delimiter helper byte d,
         and the escape helper byte e.

      Procedures:
         * Note: A 'message' is an array of bytes
        To 'escapify'   a message, search/replace (E with Ee) and (D with Ed)
        To 'unescapify' a message, search/replace (Ee with E) and (Ed with D)

      The goal of 'escapifying' a message is to turn a string of bytes into a string of bytes that's guarenteed not to contain D, which lets us use D to split multiple messages from a stream

       * Note: Not all received serial messages are valid. For example, if a raw message ends with E, it is invalid (because E must always be followed by either e or d)
           If an invalid message is received, it should be discarded.
           Regex should fully match the given message: ([^E]|(Ee)|(Ed))*
       * Note: The unescaped message is NEVER larger than the escaped message. The escaped message is either equal or larger in size. Therefore, the escaped message can be modified in-place, saving memory on an arduino (so we don't have to make a second copy)
       * Note: The size of the unescaped message is the size of the escaped message minus the number of E's in the escaped message

  I have tested this code, but I don't know how to include those tests in this file without making it really mucky and eating up the Arduino's program memory. I'll leave unit tests for another day...
  Note that it will *ignore* any messages that are longer than the buffer size, until it hears a new delimiter.
  Best practice: Send delimiters before and after your message, so if something gets corrupted in the first message, your second message will still be sent properly
*/

#ifndef ESCAPER_H //No need for a header file; this file has no dependencies
#define ESCAPER_H

//DELIMITER, ESCAPE, DELIMITER_HELMPER and ESCAPE_HELPER must all be unique
const char DELIMITER       ='\n';//'D';//'\n';//
const char ESCAPE          ='\\';//'E';//'\\';//
const char DELIMITER_HELPER='n' ;//'d';//'n' ;//    //...although it's ok (and optional) for DELIMITER_HELPER==ESCAPE xor ESCAPE_HELPER==ESCAPE
const char ESCAPE_HELPER   ='\\';//'e';//'\\';//
const unsigned int UNESCAPER_BUFFER_SIZE=1024;//The max unescaped message length. Bigger number takes up more memory but allows longer messages.

class Unescaper
{
  private:
    bool escape=false;
    bool valid =true ;//If at some point we overflowed, or made some regex error along the way that can't possibly be fixed before DELIMITER arrives
    bool start =true ;
    inline void reset()
    {
        escape=false;
        start =true ;
        valid =true ;
    }
  public:
    char buffer[UNESCAPER_BUFFER_SIZE];
    unsigned int length=0;

    bool feed(char c)
    {
        if(start)
        {
            length=0;
            start=false;
        }
        if(c==DELIMITER)
        {
            if(valid and not escape)
            {
                reset();
                return true;
            }
            else
            {
                reset();
                return false;
            }
        }
        else
        {
            if(valid)
            {
                if(length>=UNESCAPER_BUFFER_SIZE)
                {
                    //You're overflowing the buffer (the message is too big)...
                    valid=false;
                }
                else if(escape)
                {
                    escape=false;
                    switch(c)
                    {
                        case DELIMITER_HELPER: buffer[length++]=DELIMITER; break;
                        case ESCAPE_HELPER   : buffer[length++]=ESCAPE   ; break;
                        default              : valid           =false    ; break;
                    }
                }
                else if(c==ESCAPE)
                {
                    escape=true;
                }
                else
                {
                    buffer[length++]=c;
                }
            }
            return false;
        }
    }

    void feed(char *characters,
              unsigned int size,
              void handler(char *buffer,unsigned int length))
    {
        //The handler might be called multiple times given a string of characters
        //This is meant for feeding a serial fragment
        while(size--)
        {
            char c=*(characters++);
            if(feed(c))
            {
                handler(buffer,length);
            }
        }
    }

    void feed(char         read     (void),
              unsigned int available(void), 
              void         handler  (char *buffer,unsigned int length))
    {
        //Originally designed for Arduino's Serial.read, Serial.available, and a custom handler
        //Will read until there's no more bytes to read from
        //read() should return one char
        //available() should return the number of chars we can read (0 if there are no bytes to read)
        //handler(buffer,length) should do something with a byte-array with that length
        while(available())
        {
            char c=read();
            if(feed(c))
            {
                handler(buffer,length);
            }
        }
    }
};

void escapeAndSendMessage(void send(char),
                          char*message,
                          unsigned int length)
{
    //Send should be something like Serial.write(char)
    //Given an unescaped message, send a whole escaped message
    //(this function runs with constant memory, as opposed to writing a new string and sending that)
    while(length--)
    {
        char c=*(message++);
        switch(c)
        {
            case DELIMITER: send(ESCAPE); send(DELIMITER_HELPER); break;
            case ESCAPE   : send(ESCAPE); send(ESCAPE_HELPER   ); break;
            default       : send(c     );
        }
    }
}

#endif


Unescaper unescaper;

char SerialRead()
{
  return Serial.read();
}

unsigned int SerialAvailable()
{
  return Serial.available();
}

void SerialWrite(char c)
{
  Serial.write(c);
}

void handler(char*buffer,unsigned int length)
{
  Serial.print("GOT LENGTH: ");
  Serial.print(length);
  Serial.print(" : ");
  //escapeAndSendMessage(SerialWrite,buffer,length);
  for(int i=0;i<length;i++)
  {
    Serial.print(*buffer);
    buffer++;
  }
  Serial.println();
}

void loop() 
{
  unescaper.feed(SerialRead,SerialAvailable,handler);
}

void setup() 
{
  Serial.begin(115200);
}

