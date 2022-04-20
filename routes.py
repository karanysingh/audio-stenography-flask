from fileinput import filename
from flask import Flask,render_template,request,redirect,send_from_directory,send_file
# from werkzeug import secure_filename
import wave,os,time,zipfile
import tempfile

from steno import encode,decode,phase_encode,phase_decode
from img_en import lsbimg_decode,lsbimg_encode,mask
from text_en import txt_encode,txt_decode
app = Flask(__name__)

uploads_dir = tempfile.gettempdir()

os.makedirs(os.path.join(uploads_dir,"steno"), exist_ok=True)
uploads_dir = os.path.join(uploads_dir,"steno")

@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method == 'GET':
        return render_template('./index.html')
    elif request.method == 'POST':
        # file = request.args
        # audio = wave.open(file,mode="rb")
        # print(request)
        # encode(audio)
        return redirect('/')

@app.route('/upload',methods=['POST'])
def upload():
    if request.method == 'POST':
        
        profile = request.files['file']
        # path = os.path.join(uploads_dir, secure_filename(profile.filename))
        path = os.path.join(uploads_dir, profile.filename)

        print(list(request.form.keys()))
        type = request.form['type']
 
        profile.save(path)
        # print("Saved ",message)
# IMAGE STEGANOGRAPHY
        if(type in ["lsbimg","mask","enimg"]):
            if(type=="lsbimg"):
                message = request.form['message']
                lsbimg_encode(path,message)
            elif(type=="mask"):        
                maskpath = os.path.join(uploads_dir, request.files['maskfile'].filename)
                request.files['maskfile'].save(maskpath)
                
                print("maskpath: ",maskpath)
                mask(path,maskpath)
            else:
                pass
            return send_file(
    os.path.join(uploads_dir,profile.filename),
        # mimetype = 'png',
        attachment_filename= profile.filename[:-4]+"_encoded"+profile.filename[-4:],
        as_attachment = True)
            
# AUDIO STEGANOGRAPHY   

        elif(type in ["phase","lsb","parity"]):
            audio = wave.open(path,mode="rb")
            # print("Opened")
            
            # encode(audio,profile.filename,message)
            if(type=="phase"):
                        
                message = request.form['message']
                phase_encode(audio,path,profile.filename,message)
            elif(type=="lsb"):
                message = request.form['message']
                encode(audio,profile.filename,message)
            # print("Encoded")
            
            return send_file(os.path.join(uploads_dir,profile.filename+"encoded"),
                mimetype = 'wav',
                attachment_filename= profile.filename+"_encoded.wav",
                as_attachment = True)
            
# TEXT STEGANOGRAPHY
        elif(type in ["snow","lookalike","zw"]):
            f = open(path, "r")
            data = f.read()
            f.close()
            message = request.form['message']
            if(type=="zero"):
                new_data = txt_encode(data,message.encode("ascii"),"zw",binary=True)
            
            elif(type=="snow"):
                new_data = txt_encode(data,message.encode("ascii"),"snow",binary=True)
            else:
                new_data = txt_encode(data,message.encode("ascii"),"lookalike",binary=True)
            with open(path+"_encoded", "w", encoding="utf-8") as f:
                f.write(new_data)
                f.close()
            return send_file(os.path.join(uploads_dir,profile.filename+"_encoded"),
                mimetype = 'txt',
                attachment_filename= profile.filename+"_encoded.txt",
                as_attachment = True)
        # return send_from_directory(os.path.join(uploads_dir, 'sampleStego.wav'),filename="encoded.wav",as_attachment=True)
    else:
        return redirect('/')



@app.route('/decode',methods=['POST'])
def decoder():
    if request.method == 'POST':
        
        profile = request.files['file']
        type = request.form['type']

        # path = os.path.join(uploads_dir, secure_filename(profile.filename))
        path = os.path.join(uploads_dir,profile.filename)
        # setupdir(path)
        # os.mkdir(path)
        
        profile.save(path)
        # print("Saved")
        
# IMAGE STEGANOGRAPHY
        if(type in ["lsbimg","rpeimg","enimg"]):
            if(type=="lsbimg"):
                text = lsbimg_decode(path)
                print("got text",text)
            elif(type=="mask"):
                pass
            else:
                pass
        elif(type in ["phase","lsb","parity"]):
            audio = wave.open(path,mode="rb")
            # print("Opened")
            if(type=="phase"):
                text = phase_decode(audio,profile.filename,path)
            elif(type=="lsb"):
                text = decode(audio,profile.filename)

# TEXT STEGANOGRAPHY
        elif(type in ["snow","lookalike","zw"]):
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
                f.close()
            text = txt_decode(data,type,binary=True)
            print("decoded==> ",str(text))
            
        return render_template('./index.html', deciphered=text)
    else:
        return redirect('/')
    




# def setupdir(uploads_dir):
#     try:
#         os.rmdir(uploads_dir)
#         print("Directory '% s' has been removed successfully" % uploads_dir)
#     except OSError as error:
#         print(error)
#         print("Directory '% s' can not be removed" % uploads_dir)
        