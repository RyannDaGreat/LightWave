struct CharBufferReader
{
	// This is a custom reader class to let ArduinoJson parse MsgPack into a JsonDocument
	// It's meant to work with my Escaper class's buffer
	// Documentation: https://arduinojson.org/v6/api/msgpack/deserializemsgpack/

	char * src_buffer       ;
	size_t src_length       ;
	size_t cursor_index     ;
	CharBufferReader(char*src_buffer,size_t src_length)
	{
		this.src_buffer       =src_buffer       ;
		this.src_length       =src_length       ;
		this.cursor_index     =0                ;
	}

	int read()
	{
		// Reads one byte, or returns -1
		if(cursor_index>=src_length)
		{
			return -1;
		}
		return src_buffer[cursor_index++];
	}

	size_t readBytes(char* dst_buffer, size_t read_length)
	{
		// Reads several bytes, returns the number of bytes read.
		if(cursor_index>=src_length)
		{
			return 0;//We've allready read the whole buffer, so we return 0 because we've read 0 bytes
		}
		int unread_length=src_length-cursor_index;
		if(read_length>unread_length)
		{
			read_length=unread_length;
		}
		while(read_length--)
		{
			*(dst_buffer++)=src_buffer[cursor_index++];
		}
		return read_length;
	}
};