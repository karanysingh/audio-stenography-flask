from flask import Flask,render_template,request,redirect,send_from_directory,send_file
# from werkzeug import secure_filename
import wave,os,time,zipfile
import tempfile

from steno import encode,decode,phase_encode,phase_decode
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

        # print(request.args)
        message = request.form['message']
        type = request.form['type']
        
        profile.save(path)
        # print("Saved")
    
        audio = wave.open(path,mode="rb")
        # print("Opened")
        
        # encode(audio,profile.filename,message)
        if(type=="phase"):
            phase_encode(audio,path,profile.filename,message)
        elif(type=="lsb"):
            encode(audio,profile.filename,message)
        # print("Encoded")
        
        return send_file(os.path.join(uploads_dir,profile.filename+"encoded"),
            mimetype = 'wav',
            attachment_filename= profile.filename+"_encoded.wav",
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
    
        audio = wave.open(path,mode="rb")
        # print("Opened")
        if(type=="phase"):
            text = phase_decode(audio,profile.filename,path)
        elif(type=="lsb"):
            text = decode(audio,profile.filename)
        # print("Decoded")
    
        return render_template('./index.html', deciphered=text)
        # return send_from_directory(os.path.join(uploads_dir, 'sampleStego.wav'),filename="encoded.wav",as_attachment=True)
    else:
        return redirect('/')



# def setupdir(uploads_dir):
#     try:
#         os.rmdir(uploads_dir)
#         print("Directory '% s' has been removed successfully" % uploads_dir)
#     except OSError as error:
#         print(error)
#         print("Directory '% s' can not be removed" % uploads_dir)
        