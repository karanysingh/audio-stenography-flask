import wave,tempfile,os
import numpy as np
import scipy as sp
import scipy.io.wavfile

uploads_dir = tempfile.gettempdir()
uploads_dir = os.path.join(uploads_dir,"steno")

def phase_encode(audio,path,filename,string):
  print("\nPhase Encoding Starts..")
  # rate, channels = sp.io.wavfile.read(audio)
  rate, audioData1 = sp.io.wavfile.read(path)
  stringToEncode = string.ljust(100, '~')
  textLength = 8 * len(stringToEncode)
  print(rate)
  chunkSize = int(2 * 2 ** np.ceil(np.log2(2 * textLength)))
  numberOfChunks = int(np.ceil(audioData1.shape[0] / chunkSize))
  audioData = audioData1.copy()

  #Breaking the Audio into chunks
  if len(audioData1.shape) == 1:
      audioData.resize(numberOfChunks * chunkSize, refcheck=False)
      audioData = audioData[np.newaxis]
  else:
      audioData.resize((numberOfChunks * chunkSize, audioData.shape[1]), refcheck=False)
      audioData = audioData.T

  chunks = audioData[0].reshape((numberOfChunks, chunkSize))

  #Applying DFT on audio chunks
  chunks = np.fft.fft(chunks)
  magnitudes = np.abs(chunks)
  phases = np.angle(chunks)
  phaseDiff = np.diff(phases, axis=0)
  # Convert message to encode into binary
  textInBinary = np.ravel([[int(y) for y in format(ord(x), "08b")] for x in stringToEncode])

  # Convert message in binary to phase differences
  textInPi = textInBinary.copy()
  textInPi[textInPi == 0] = -1
  textInPi = textInPi * -np.pi / 2
  midChunk = chunkSize // 2

  # Phase conversion
  phases[0, midChunk - textLength: midChunk] = textInPi
  phases[0, midChunk + 1: midChunk + 1 + textLength] = -textInPi[::-1]

  # Compute the phase matrix
  for i in range(1, len(phases)):
      phases[i] = phases[i - 1] + phaseDiff[i - 1]
      
  # Apply Inverse fourier trnasform after applying phase differences
  chunks = (magnitudes * np.exp(1j * phases))
  chunks = np.fft.ifft(chunks).real
    # Combining all block of audio again
  audioData[0] = chunks.ravel().astype(np.int16)    

  dir = os.path.dirname(path)
  sp.io.wavfile.write(path + "encoded", rate, audioData.T)
  print("stored at ", path + "encoded")
  

def phase_decode(audio,filename,path):
  rate, audioData = sp.io.wavfile.read(path)
  print(rate)
  textLength = 800
  blockLength = 2 * int(2 ** np.ceil(np.log2(2 * textLength)))
  blockMid = blockLength // 2
  print(blockLength, blockMid)
  # Get header info
  if len(audioData.shape) == 1:
      code = audioData[:blockLength]
  else:
      code = audioData[:blockLength, 0]
  print(code)
  # Get the phase and convert it to binary
  codePhases = np.angle(np.fft.fft(code))[blockMid - textLength:blockMid]
  codeInBinary = (codePhases < 0).astype(np.int16)

  # Convert into characters
  codeInIntCode = codeInBinary.reshape((-1, 8)).dot(1 << np.arange(8 - 1, -1, -1))
  
  # Combine characters to original text
  return "".join(np.char.mod("%c", codeInIntCode)).replace("~", "")
  print(tmp)
  print("decoding")
  return tmp

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