#THIS PACKAGE HAS BEEN MODIFIED BY RYAN BURGERT 2019 FOR MICROPYTHON
#CHANGES:
#   (Many changes here were made to reduce the amount of memory this code takes up. The actual functions themselves took too much memory...and led to unreadable code (because there was so much stuff I didnt need))
#   Removal of any reference to the datetime library (which is not in micropython)
#   Removal of any reference to the collections library (which is not in micropython)
#   Removal of Python2 compatiability (saves memory)
#   Removed 'compatiability mode', which provided compatiability to older versions of msgpack. It's not needed, and takes up more memory.
#   Removed support for "ext" handlers, because I don't think I'll ever use them. (I saved a version of this code before I deleted that support though)
#   TODO: Replace the chains of 9-or-more 'if/elif' blocks with dict lookups. After profiling it in micropython, I confirmed it is definitiely faster for n>=2 (see https://gist.github.com/SqrtRyan/db995c2a65ba08d88bfca55c38336cc5)

# u-msgpack-python v2.5.2 - v at sergeev.io
# https://github.com/vsergeev/u-msgpack-python
#
# u-msgpack-python is a lightweight MessagePack serializer and deserializer
# module, compatible with both Python 2 and 3, as well CPython and PyPy
# implementations of Python. u-msgpack-python is fully compliant with the
# latest MessagePack specification.com/msgpack/msgpack/blob/master/spec.md). In
# particular, it supports the new binary, UTF-8 string, and application ext
# types.
"""
u-msgpack-python v2.5.2 - v at sergeev.io
https://github.com/vsergeev/u-msgpack-python
u-msgpack-python is a lightweight MessagePack serializer and deserializer
module, compatible with both Python 2 and 3, as well CPython and PyPy
implementations of Python. u-msgpack-python is fully compliant with the
latest MessagePack specification.com/msgpack/msgpack/blob/master/spec.md). In
particular, it supports the new binary, UTF-8 string, and application ext
types.
License: MIT
__version__ = "2.5.2"#Module version string
version = (2, 5, 2)  #Module version tuple
"""

import struct,collections,sys,io

class InvalidString(bytes):
    """Subclass of bytes to hold invalid UTF-8 strings."""
    pass

##############################################################################
# Exceptions
##############################################################################

# Base Exception classes
class PackException(Exception):
    "Base class for exceptions encountered during packing."
    pass

class UnpackException(Exception):
    "Base class for exceptions encountered during unpacking."
    pass

# Packing error
class UnsupportedTypeException(PackException):
    "Object type not supported for packing."
    pass

# Unpacking error
class InsufficientDataException(UnpackException):
    "Insufficient data to unpack the serialized object."
    pass

class InvalidStringException(UnpackException):
    "Invalid UTF-8 string encountered during unpacking."
    pass

class ReservedCodeException(UnpackException):
    "Reserved code encountered during unpacking."
    pass

class UnhashableKeyException(UnpackException):
    """
    Unhashable key encountered during map unpacking.
    The serialized map cannot be deserialized into a Python dictionary.
    """
    pass

class DuplicateKeyException(UnpackException):
    "Duplicate key encountered during map unpacking."
    pass

#############################################################################
# Exported Functions and Glob
#############################################################################

# Exported functions and variables, set up in __init()

##############################################################################
# Packing
##############################################################################

# You may notice struct.pack("B", obj) instead of the simpler chr(obj) in the
# code below. This is to allow for seamless Python 2 and 3 compatibility, as
# chr(obj) has a str return type instead of bytes in Python 3, and
# struct.pack(...) has the right return type in both versions.


def _pack_integer(obj, fp, options):
    if obj < 0:
        if   obj >= -32         :fp.write(struct.pack("b", obj))
        elif obj >= -2**( 8 - 1):fp.write(b"\xd0" + struct.pack( "b", obj))
        elif obj >= -2**(16 - 1):fp.write(b"\xd1" + struct.pack(">h", obj))
        elif obj >= -2**(32 - 1):fp.write(b"\xd2" + struct.pack(">i", obj))
        elif obj >= -2**(64 - 1):fp.write(b"\xd3" + struct.pack(">q", obj))
        else:
            raise UnsupportedTypeException("huge signed int")
    else:
        if   obj <   128:fp.write(struct.pack("B", obj))
        elif obj < 2** 8:fp.write(b"\xcc" + struct.pack( "B", obj))
        elif obj < 2**16:fp.write(b"\xcd" + struct.pack(">H", obj))
        elif obj < 2**32:fp.write(b"\xce" + struct.pack(">I", obj))
        elif obj < 2**64:fp.write(b"\xcf" + struct.pack(">Q", obj))
        else:
            raise UnsupportedTypeException("huge unsigned int")


def _pack_nil(obj, fp, options):
    fp.write(b"\xc0")


def _pack_boolean(obj, fp, options):
    fp.write(b"\xc3" if obj else b"\xc2")


def _pack_float(obj, fp, options):
    float_precision = options.get('force_float_precision', _float_precision)

    if   float_precision == "double":fp.write(b"\xcb" + struct.pack(">d", obj))
    elif float_precision == "single":fp.write(b"\xca" + struct.pack(">f", obj))
    else:
        raise ValueError("invalid float precision")


def _pack_string(obj, fp, options):
    obj = obj.encode('utf-8')
    obj_len = len(obj)
    if   obj_len <    32:fp.write(struct.pack("B", 0xa0 | obj_len) + obj)
    elif obj_len < 2** 8:fp.write(b"\xd9" + struct.pack( "B", obj_len) + obj)
    elif obj_len < 2**16:fp.write(b"\xda" + struct.pack(">H", obj_len) + obj)
    elif obj_len < 2**32:fp.write(b"\xdb" + struct.pack(">I", obj_len) + obj)
    else:
        raise UnsupportedTypeException("huge string")


def _pack_binary(obj, fp, options):
    obj_len = len(obj)
    if   obj_len < 2** 8:fp.write(b"\xc4" + struct.pack( "B", obj_len) + obj)
    elif obj_len < 2**16:fp.write(b"\xc5" + struct.pack(">H", obj_len) + obj)
    elif obj_len < 2**32:fp.write(b"\xc6" + struct.pack(">I", obj_len) + obj)
    else:
        raise UnsupportedTypeException("huge binary string")


def _pack_oldspec_raw(obj, fp, options):
    obj_len = len(obj)
    if   obj_len <    32:fp.write(struct.pack("B", 0xa0 | obj_len) + obj)
    elif obj_len < 2**16:fp.write(b"\xda" + struct.pack(">H", obj_len) + obj)
    elif obj_len < 2**32:fp.write(b"\xdb" + struct.pack(">I", obj_len) + obj)
    else:
        raise UnsupportedTypeException("huge raw string")

def _pack_array(obj, fp, options):
    obj_len = len(obj)
    if   obj_len <    16:fp.write(struct.pack("B", 0x90 | obj_len))
    elif obj_len < 2**16:fp.write(b"\xdc" + struct.pack(">H", obj_len))
    elif obj_len < 2**32:fp.write(b"\xdd" + struct.pack(">I", obj_len))
    else:
        raise UnsupportedTypeException("huge array")

    for e in obj:
        pack(e, fp, **options)


def _pack_map(obj, fp, options):
    obj_len = len(obj)
    if   obj_len <    16:fp.write(struct.pack("B", 0x80 | obj_len))
    elif obj_len < 2**16:fp.write(b"\xde" + struct.pack(">H", obj_len))
    elif obj_len < 2**32:fp.write(b"\xdf" + struct.pack(">I", obj_len))
    else:
        raise UnsupportedTypeException("huge array")

    for k, v in obj.items():
        pack(k, fp, **options)
        pack(v, fp, **options)

########################################

# Pack for Python 3, with unicode 'str' type, 'bytes' type, and no 'long' type

_pack_lookup_table={
    type(None):_pack_nil,
    bool      :_pack_boolean,
    int       :_pack_integer,
    float     :_pack_float,
    str       :_pack_string,
    bytes     :_pack_binary,
    list      :_pack_array,
    tuple     :_pack_array,
    dict      :_pack_map,
}

def pack(obj, fp, **options):
    """
    Serialize a Python object into MessagePack bytes.
    Args:
        obj: a Python object
        fp: a .write()-supporting file-like object
    Kwargs:
        force_float_precision (str): "single" to force packing floats as
                                     IEEE-754 single-precision floats,
                                     "double" to force packing floats as
                                     IEEE-754 double-precision floats.
    Returns:
        None.
    Raises:
        UnsupportedType(PackException):
            Object type not supported for packing.
    Example:
    >>> f = open('test.bin', 'wb')
    >>> umsgpack.pack({u"compact": True, u"schema": 0}, f)
    >>>
    """

    _pack_lookup_table[type(obj)](obj,fp,options)

    #OLDER CODE:
    # if obj is None                                      :_pack_nil(obj, fp, options)
    # elif isinstance(obj, bool)                          :_pack_boolean(obj, fp, options)
    # elif isinstance(obj, int)                           :_pack_integer(obj, fp, options)
    # elif isinstance(obj, float)                         :_pack_float(obj, fp, options)
    # elif isinstance(obj, str)                           :_pack_string(obj, fp, options)
    # elif isinstance(obj, bytes)                         :_pack_binary(obj, fp, options)
    # elif isinstance(obj, list)                          :_pack_array(obj, fp, options)
    # elif isinstance(obj, tuple)                         :_pack_array(obj, fp, options)
    # elif isinstance(obj, dict)                          :_pack_map(obj, fp, options)

def packb(obj, **options):
    """
    Serialize a Python object into MessagePack bytes.
    Args:
        obj: a Python object
    Kwargs:
        force_float_precision (str): "single" to force packing floats as
                                     IEEE-754 single-precision floats,
                                     "double" to force packing floats as
                                     IEEE-754 double-precision floats.
    Returns:
        A 'bytes' containing serialized MessagePack bytes.
    Raises:
        UnsupportedType(PackException):
            Object type not supported for packing.
    Example:
    >>> umsgpack.packb({u"compact": True, u"schema": 0})
    b'\x82\xa7compact\xc3\xa6schema\x00'
    >>>
    """
    fp = io.BytesIO()
    pack(obj, fp, **options)
    return fp.getvalue()

#############################################################################
# Unpacking
#############################################################################

def _read_except(fp, n):
    if n == 0:
        return b""

    data = fp.read(n)
    if len(data) == 0:
        raise InsufficientDataException()

    while len(data) < n:
        chunk = fp.read(n - len(data))
        if len(chunk) == 0:
            raise InsufficientDataException()

        data += chunk

    return data

def _unpack_integer(code, fp, options):
    if   code == b'\xd0'           :return struct.unpack( "b", _read_except(fp, 1))[0]
    elif code == b'\xd1'           :return struct.unpack(">h", _read_except(fp, 2))[0]
    elif code == b'\xd2'           :return struct.unpack(">i", _read_except(fp, 4))[0]
    elif code == b'\xd3'           :return struct.unpack(">q", _read_except(fp, 8))[0]
    elif code == b'\xcc'           :return struct.unpack( "B", _read_except(fp, 1))[0]
    elif code == b'\xcd'           :return struct.unpack(">H", _read_except(fp, 2))[0]
    elif code == b'\xce'           :return struct.unpack(">I", _read_except(fp, 4))[0]
    elif code == b'\xcf'           :return struct.unpack(">Q", _read_except(fp, 8))[0]
    elif (ord(code) & 0xe0) == 0xe0:return struct.unpack( "b", code               )[0]
    elif (ord(code) & 0x80) == 0x00:return struct.unpack( "B", code               )[0]
    raise Exception("logic error, not int: 0x%02x" % ord(code))

def _unpack_reserved(code, fp, options):
    if code == b'\xc1':
        raise ReservedCodeException(
            "encountered reserved code: 0x%02x" % ord(code))
    raise Exception(
        "logic error, not reserved code: 0x%02x" % ord(code))

def _unpack_nil(code, fp, options):
    if code == b'\xc0':return None
    raise Exception("logic error, not nil: 0x%02x" % ord(code))

def _unpack_boolean(code, fp, options):
    if   code == b'\xc2':return False
    elif code == b'\xc3':return True
    raise Exception("logic error, not boolean: 0x%02x" % ord(code))

def _unpack_float(code, fp, options):
    if code == b'\xca'  :return struct.unpack(">f", _read_except(fp, 4))[0]
    elif code == b'\xcb':return struct.unpack(">d", _read_except(fp, 8))[0]
    raise Exception("logic error, not float: 0x%02x" % ord(code))

def _unpack_string(code, fp, options):
    if (ord(code) & 0xe0) == 0xa0:length = ord(code) & ~0xe0
    elif code == b'\xd9'         :length = struct.unpack( "B", _read_except(fp, 1))[0]
    elif code == b'\xda'         :length = struct.unpack(">H", _read_except(fp, 2))[0]
    elif code == b'\xdb'         :length = struct.unpack(">I", _read_except(fp, 4))[0]
    else:
        raise Exception("logic error, not string: 0x%02x" % ord(code))

    data = _read_except(fp, length)
    try:
        return bytes.decode(data, 'utf-8')
    except UnicodeDecodeError:
        if options.get("allow_invalid_utf8"):
            return InvalidString(data)
        raise InvalidStringException("unpacked string is invalid utf-8")

def _unpack_binary(code, fp, options):
    if   code == b'\xc4':length = struct.unpack( "B", _read_except(fp, 1))[0]
    elif code == b'\xc5':length = struct.unpack(">H", _read_except(fp, 2))[0]
    elif code == b'\xc6':length = struct.unpack(">I", _read_except(fp, 4))[0]
    else:
        raise Exception("logic error, not binary: 0x%02x" % ord(code))

    return _read_except(fp, length)

def _unpack_array(code, fp, options):
    if   code == b'\xdc'         :length = struct.unpack(">H", _read_except(fp, 2))[0],
    elif code == b'\xdd'         :length = struct.unpack(">I", _read_except(fp, 4))[0]
    elif (ord(code) & 0xf0) == 0x90:length = (ord(code) & ~0xf0)
    else:
        raise Exception("logic error, not array: 0x%02x" % ord(code))

    return [_unpack(fp, options) for i in range(length)]

def _deep_list_to_tuple(obj):
    if isinstance(obj, list):
        return tuple([_deep_list_to_tuple(e) for e in obj])
    return obj

def _unpack_map(code, fp, options):
    if (ord(code) & 0xf0) == 0x80:
        length = (ord(code) & ~0xf0)
    elif code == b'\xde':
        length = struct.unpack(">H", _read_except(fp, 2))[0]
    elif code == b'\xdf':
        length = struct.unpack(">I", _read_except(fp, 4))[0]
    else:
        raise Exception("logic error, not map: 0x%02x" % ord(code))

    d = {}

    for _ in range(length):
        # Unpack key
        k = _unpack(fp, options)

        if isinstance(k, list):
            # Attempt to convert list into a hashable tuple
            k = _deep_list_to_tuple(k)
        #RYAN BURGERT: Commented this out because micropython doesn't have a collections library, which is where Hashable comes from
        #elif not isinstance(k, Hashable):
        #    raise UnhashableKeyException(
        #        "encountered unhashable key: %s, %s" % (str(k), str(type(k))))
        elif k in d:
            raise DuplicateKeyException(
                "encountered duplicate key: %s, %s" % (str(k), str(type(k))))

        # Unpack value
        v = _unpack(fp, options)

        try:
            d[k] = v
        except TypeError:
            raise UnhashableKeyException(
                "encountered unhashable key: %s" % str(k))
    return d


def _unpack(fp, options):
    code = _read_except(fp, 1)
    return _unpack_dispatch_table[code](code, fp, options)

def unpack(fp, **options):
    """
    Deserialize MessagePack bytes into a Python object.
    Args:
        fp: a .read()-supporting file-like object
    Kwargs:
        allow_invalid_utf8 (bool): unpack invalid strings into instances of
                                   InvalidString, for access to the bytes
                                   (default False)
    Returns:
        A Python object.
    Raises:
        InsufficientDataException(UnpackException):
            Insufficient data to unpack the serialized object.
        InvalidStringException(UnpackException):
            Invalid UTF-8 string encountered during unpacking.
        ReservedCodeException(UnpackException):
            Reserved code encountered during unpacking.
        UnhashableKeyException(UnpackException):
            Unhashable key encountered during map unpacking.
            The serialized map cannot be deserialized into a Python dictionary.
        DuplicateKeyException(UnpackException):
            Duplicate key encountered during map unpacking.
    Example:
    >>> f = open('test.bin', 'rb')
    >>> umsgpack.unpackb(f)
    {'compact': True, 'schema': 0}
    >>>
    """
    return _unpack(fp, options)

# For Python 3, expects a bytes object
def unpackb(s, **options):
    """
    Deserialize MessagePack bytes into a Python object.
    Args:
        s: a 'bytes' or 'bytearray' containing serialized MessagePack bytes
    Kwargs:
        allow_invalid_utf8 (bool): unpack invalid strings into instances of
                                   InvalidString, for access to the bytes
                                   (default False)
    Returns:
        A Python object.
    Raises:
        TypeError:
            Packed data type is neither 'bytes' nor 'bytearray'.
        InsufficientDataException(UnpackException):
            Insufficient data to unpack the serialized object.
        InvalidStringException(UnpackException):
            Invalid UTF-8 string encountered during unpacking.
        ReservedCodeException(UnpackException):
            Reserved code encountered during unpacking.
        UnhashableKeyException(UnpackException):
            Unhashable key encountered during map unpacking.
            The serialized map cannot be deserialized into a Python dictionary.
        DuplicateKeyException(UnpackException):
            Duplicate key encountered during map unpacking.
    Example:
    >>> umsgpack.unpackb(b'\x82\xa7compact\xc3\xa6schema\x00')
    {'compact': True, 'schema': 0}
    >>>
    """
    if not isinstance(s, (bytes, bytearray)):
        raise TypeError("packed data must be type 'bytes' or 'bytearray'")
    return _unpack(io.BytesIO(s), options)

#############################################################################
# Module Initialization
#############################################################################

# Auto-detect system float precision
#THIS FAILS ON MICROPYTHON. I'll just set it to "single" to save space...
#if sys.float_info.mant_dig == 53:
#    _float_precision = "double"
#else:
#    _float_precision = "single"
_float_precision = "single"

_unpack_dispatch_table = {}      # Build a dispatch table for fast lookup of unpacking function. len(_unpack_dispatch_table)==256, maps chars to functions
for code in range(0   , 0x7f + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_integer# Fix uint
for code in range(0x80, 0x8f + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_map    # Fix map
for code in range(0x90, 0x9f + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_array  # Fix array
for code in range(0xa0, 0xbf + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_string # Fix str
for code in range(0xc4, 0xc6 + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_binary # Bin
for code in range(0xcc, 0xcf + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_integer# Uint
for code in range(0xd0, 0xd3 + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_integer# Int
for code in range(0xd9, 0xdb + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_string # String
for code in range(0xe0, 0xff + 1):_unpack_dispatch_table[struct.pack("B", code)] = _unpack_integer# Negative fixint

_unpack_dispatch_table[b'\xc0'] = _unpack_nil     # Nil
_unpack_dispatch_table[b'\xc1'] = _unpack_reserved# Reserved
_unpack_dispatch_table[b'\xc2'] = _unpack_boolean # Boolean
_unpack_dispatch_table[b'\xc3'] = _unpack_boolean # Boolean
_unpack_dispatch_table[b'\xdc'] = _unpack_array   # Array
_unpack_dispatch_table[b'\xdd'] = _unpack_array   # Array
_unpack_dispatch_table[b'\xde'] = _unpack_map     # Map
_unpack_dispatch_table[b'\xdf'] = _unpack_map     # Map
_unpack_dispatch_table[b'\xca'] = _unpack_float   # Float
_unpack_dispatch_table[b'\xcb'] = _unpack_float   # Float

__all__=[
##Functions
'pack',
'packb',
'unpack',
'unpackb',
##Exceptions
'InvalidString',
'PackException',
'UnpackException',
'UnsupportedTypeException',
'InsufficientDataException',
'InvalidStringException',
'ReservedCodeException',
'UnhashableKeyException',
'DuplicateKeyException',
]