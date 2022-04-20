import re
from helper import snow_encode,snow_decode,emoji_encode,emoji_decode,subs_encode,subs_decode,zw_encode,zw_decode,zwc_4


def txt_encode(unencoded_string, msg, method="zw", binary=False, replacements=None, delimiter=None):
    '''
    Main encoding method
    Dispatches to corresponding encoder based on specified method and handles
    insertion/appending etc. of message into the string.
    '''
    if method == "zw":
        
        code = zw_encode(msg, character_set=replacements, binary=binary)
        chars = list(unencoded_string)
        split_code = [code[i:i+4] for i in range(0, len(code), 4)]

        if len(split_code) >= len(chars):
            raise ValueError("String too short to encode message")

        out = ''
        for i in range(len(chars)):
            out = out + chars[i]
            if i < len(split_code):
                out = out + split_code[i]

        return out

    elif method == "snow":
        if not delimiter:
            delimiter = '\t\t\t'
        code = snow_encode(msg, character_set=replacements, binary=binary)
        return unencoded_string + delimiter + code

    elif method == "lookalike":
        return subs_encode(unencoded_string, msg, substitution_table=replacements, binary=binary)

    elif method == "emoji":
        return emoji_encode(msg, binary=binary)

    else:
        raise Exception("Method: {}, is not supported".format(method))


def txt_decode(encoded_string, method="zw", binary=False, replacements=None, delimiter=None):
    '''
    Main decoding method
    Dispatches to corresponding decoder based on specified method and handles
    extraction of encoded message from the string.
    '''
    if method == "zw":
        if not replacements:
            replacements = zwc_4
        code = ''
        for c in encoded_string:
            if c in replacements:
                code = code + c

        return zw_decode(code, character_set=replacements, binary=binary)

    elif method == "snow":
        if not delimiter:
            delimiter = '\t\t\t'
        regex = "{}(.+)$".format(delimiter)
        m = re.search(regex, encoded_string)
        code = m.groups()[0]

        return snow_decode(code, character_set=replacements, binary=binary)

    elif method == "lookalike":
        return subs_decode(encoded_string, substitution_table=replacements, binary=binary)

    elif method == "emoji":
        return emoji_decode(encoded_string, binary=binary)