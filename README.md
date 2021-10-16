# Audio Steganography
Audio Steganography is a technique used to transmit hidden information by modifying an audio signal in an imperceptible manner.

## About the project
Its the part of the information security J component

## Tech Stack
- `Flask` used to create the web-app and configure the end points.
- `Python` base language for steganography and other operations.

## Hosted at 
- https://steno-flask.herokuapp.com/

## End-points
- `POST` at /decode with form including the file with key/name `file` to get the message decoded inside the file.
- `POST` at /upload with form including the file with key/name `file` and the message with key/name `message` to get the encoded file.

## Instructions to run locally
- use `pip install -r requirements.txt` to install all the dependencies.
- use `python3 app.py` to run the project.

## Contributors
- Shrimayee
- Himanshu
- Karan

