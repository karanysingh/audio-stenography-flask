from routes import app

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 8000, threaded = True, debug = True)
    # app.run(host='127.0.0.1',port = 8000, threaded = True, debug = True)
