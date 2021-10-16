import wave,tempfile,os

uploads_dir = tempfile.gettempdir()
uploads_dir = os.path.join(uploads_dir,"steno")

def encode(audio,filename,string):
  print("\nEncoding Starts..")
  # audio = wave.open("Happy-birthday-instrumental.wav",mode="rb")
  frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
  # print(string)
  string = string + int((len(frame_bytes)-(len(string)*8*8))/8) * '#'
  bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in string])))
 
  for i, bit in enumerate(bits):
    frame_bytes[i] = (frame_bytes[i] & 254) | bit
     
  frame_modified = bytes(frame_bytes)
  for i in range(0, 10):
    print(frame_bytes[i])
   
  newAudio = wave.open(os.path.join(uploads_dir,filename+"encoded"), 'wb')
  newAudio.setparams(audio.getparams())
  newAudio.writeframes(frame_modified)

  newAudio.close()
  audio.close()
  print(" |---->succesfully encoded inside sampleStego.wav")


def decode(audio,filename):
  print("\nDecoding Starts..")
  # audio = wave.open("sampleStego.wav", mode='rb')
  frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
  extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
  string = "".join(chr(int("".join(map(str, extracted[i:i+8])), 2)) for i in range(0, len(extracted), 8))
  decoded = string.split("###")[0]
  return decoded

# print("hello")