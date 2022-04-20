snow_2 = [" ", "\t"]

def snow_encode(msg, character_set=None, binary=False):
    code = ''
    if not character_set:
        character_set = snow_2
    if binary:
        msg_bytes = msg
    else:
        msg_bytes = bytes(msg, 'utf-8')
    for by in msg_bytes:
        bit_mask = 0b00000001
        for i in range(8):
            m_byte = by & bit_mask
            by = by >> 1
            if m_byte == 1:
                code += character_set[1]
            elif m_byte == 0:
                code += character_set[0]

    return code

def snow_decode(code, character_set=None, binary=False):
    msg_bytes = []
    if not character_set:
        character_set = snow_2

    # range behave a little weird here is there a less hacky solution?
    for i in range(8, len(code)+1, 8):
        m_byte = 0b00000000
        encoded_byte = code[i-8:i]
        # for char in encoded_byte:
        #     print("char: {} ord: {}".format(char, hex(ord(char))))

        for j in range(8):
            m_byte = m_byte >> 1
            if encoded_byte[j] == character_set[1]:
                m_byte = m_byte | 0b10000000
            elif encoded_byte[j] == character_set[0]:
                pass

        msg_bytes.append(m_byte)

    if binary:
        return bytes(msg_bytes)
    return bytes(msg_bytes).decode('utf-8')


CHAR_OFFSET = 32 # skip control chars
START_EMOJI = ord('\U0001F601') 

def emoji_encode(msg, binary=False):
    '''
    Encode a message using emojis
    '''
    new_str = ''
    
    if binary:
        msg_bytes = msg
    else:
        msg_bytes = bytes(msg, 'utf-8')
    
    for b in msg_bytes:
        #print(b + START_EMOJI - CHAR_OFFSET)
        new_str = new_str + chr(b + START_EMOJI - CHAR_OFFSET)


    return new_str


def emoji_decode(msg, binary=False):
    '''
    Decode a message using emojis
    '''
    new_str = '' 
    new_bytes = b''

    for c in msg:
        if binary:
           new_bytes = new_bytes + (ord(c) - START_EMOJI + CHAR_OFFSET).to_bytes(1, byteorder='big')
        else:
            new_str = new_str + chr(ord(c) - START_EMOJI + CHAR_OFFSET)

    if binary:
        return new_bytes
    return new_str




# note: we couldn't find good lookalikes for m, t and k here so we just skip them
default_substitution_table = {"a":u"\u0430", u"b":u"\u042C", "c":u"\u03f2", "d":u"\u0501", "e":u"\u0435", 
    u"f":"\uab35", u"g":"\u0261", u"h":"\u04bb", u"i":"\u0456", u"j":"\u03f3", 
    u"l":u"\u0031", u"n":u"\u0578", u"o":u"\u03BF", u"p":u"\u0440", u"q":u"\u051B",
    u"r":u"\uab81", u"s":u"\u0455", u"u":"\u057D", u"v":"\u1d20", u"w":"\u051D", 
    u"x":"\u0445", u"y":"\u0443", u"z":"\u1d22"
    }
reversed_substitution_table = {value: key for key, value in default_substitution_table.items()}

def capacity(st, substitution_table=None):
    '''
    Unicode lookalike capacity function
    utility function to determine the total capacity of a string for encoding a message. Returns 
    capacity in bytes. Can optionally be used with custom substitution tables. 
    '''
    if not substitution_table:
        substitution_table=default_substitution_table
    return sum([1 for c in st if c in substitution_table]) // 8

def subs_encode(a, msg, substitution_table=None, binary=False):
    '''
    Unicode lookalike encode function
    substitutes any character in our input string with a corresponding 'lookalike' character
    given in our substitution table to encode a method. Each substitution is used to encode 
    a single bit. If insufficient substitutable characters in input string for given message 
    raises a valueError. Returns encoded string.
    Warning:
    if you try to encode a message into a string that already contains any of our substitution
    characters the generated string will not decode correctly.
    '''
    substitutable = []
    a = list(a)
    if substitution_table:
       reversed_table = {value: key for key, value in substitution_table.items()}
    else:
        substitution_table = default_substitution_table
        reversed_table = reversed_substitution_table
    
    # first get the indexes of substitutable letters 
    for i, x in enumerate(a):
        if x in substitution_table:
            substitutable.append(i)
    # check we have enough substitutables to encode our message 
    # assumes 1 bye per char for strings
    if len(substitutable) < len(msg)*8:
        raise ValueError("Not enough substitutable characters to encode message")

    # get the encoding type of our message 
    if binary:
        msg_bytes = msg
    else:
        msg_bytes = bytes(msg, 'utf-8')

    for index, by in enumerate(msg_bytes):
        bit_mask = 0b00000001
        for i in range(8):
            si = index*8 + i # substitutable index
            m_byte = by & bit_mask
            by = by >> 1
            if m_byte == 1:
                a[substitutable[si]] = substitution_table[a[substitutable[si]]]
            elif m_byte == 0:
                pass

    return "".join(a)

def subs_decode(a, substitution_table=None, binary=False):
    '''
    Unicode lookalike decode function
    Decodes a message from a string using a unicode substitution table. Gets the byte representation
    first, by default message bytes are returned as a utf-8 string unless the 'binary' argument 
    is specified.
    Note: there is no way to know w/o specifying the message length beforehand or using some sort 
    of delimiter where the 'message' encoded into the string ends. So by default the returned value
    from this function will always be padded out with null bytes/characters.
    '''
    substitutable = []
    msg_bytes = []
    a = list(a)
    if substitution_table:
       reversed_table = {value: key for key, value in substitution_table.items()}
    else:
        substitution_table = default_substitution_table
        reversed_table = reversed_substitution_table
    
    # first get the indexes of substitutable letters 
    for i, x in enumerate(a):
        if x in substitution_table or x in reversed_table:
            substitutable.append(i)

    # slice our substitutable chars into 8 bit chunks
    for i in range(8, len(substitutable)+1, 8):
        m_byte = 0b00000000
        encoded_byte = substitutable[i-8:i]
        # set each decoded bit into our byte
        for j in range(8):
            m_byte = m_byte >> 1
            if a[encoded_byte[j]] in reversed_table:
                m_byte = m_byte | 0b10000000
            else:
                pass

        msg_bytes.append(m_byte)

    if binary:
        return bytes(msg_bytes)
    return bytes(msg_bytes).decode('utf-8')



zwc_4 = ["\u200C", "\u200D", "\u200E", "\u200F"]

def zw_encode(msg, binary=False, character_set=None):
    '''
    Encode a message using specified set of zero width characters.
    '''
    code = ''
    if not character_set:
        character_set = zwc_4
    if binary:
        msg_bytes = msg
    else:
        msg_bytes = bytes(msg, 'utf-8')
    for by in msg_bytes:
        bit_mask = 0b00000011

        for i in range(4):
            m_byte = by & bit_mask
            by = by >> 2

            if m_byte == 3:
                code += character_set[3]
            elif m_byte == 2:
                code += character_set[2]
            elif m_byte == 1:
                code += character_set[1]
            elif m_byte == 0:
                code += character_set[0]

    return code

def zw_decode(code, binary=False, character_set=None):
    '''
    Decode a message using specified set of zero width characters.
    '''
    msg_bytes = []
    if not character_set:
        character_set = zwc_4

    # range behave a little weird here is there a less hacky solution?
    for i in range(4, len(code)+1, 4):
        m_byte = 0b00000000
        encoded_byte = code[i-4:i]

        for j in range(4):
            m_byte = m_byte >> 2
            if encoded_byte[j] == character_set[3]:
                m_byte = m_byte | 0b11000000
            elif encoded_byte[j] == character_set[2]:
                m_byte = m_byte | 0b10000000
            elif encoded_byte[j] == character_set[1]:
                m_byte = m_byte | 0b01000000
            elif encoded_byte[j] == character_set[0]:
                pass

        msg_bytes.append(m_byte)

    if binary:
        return bytes(msg_bytes)
    return bytes(msg_bytes).decode('utf-8')