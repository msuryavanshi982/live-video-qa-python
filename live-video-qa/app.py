from flask import Flask, render_template, request, jsonify
import cv2
import os
import sounddevice as sd
from scipy.io.wavfile import write

app = Flask(__name__)

# Define variables to control recording
recording_audio = False
audio_stream = None
recording_video = False
audio_filename = "interview_audio.wav"
video_filename = "interview.avi"
video_writer = None

# Function to start recording audio
def record_audio(duration=5, sample_rate=44100, channels=2):
    global recording_audio, audio_stream

    try:
        recording_audio = True
        audio_stream = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels)
        return True
    except Exception as e:
        print("Error:", e)
        return False

# Function to start and stop video recording
def toggle_video_recording():
    global recording_video, video_writer

    if not recording_video:
        recording_video = True
        video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
        cap = cv2.VideoCapture(0)
        while recording_video:
            ret, frame = cap.read()
            if not ret:
                break
            video_writer.write(frame)
        cap.release()
        video_writer.release()
        recording_video = False
        video_writer = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record', methods=['POST'])
def record():
    global recording_audio, audio_stream
    data = request.json

    if data['action'] == 'start':
        success = record_audio(duration=3600)
        toggle_video_recording()
        if success:
            recording_audio = True
            return jsonify({'status': 'started'})
        else:
            return jsonify({'status': 'error'})
    elif data['action'] == 'stop':
        recording_audio = False
        if audio_stream is not None:
            sd.wait()
            write(audio_filename, 44100, audio_stream)
            audio_stream = None
        return jsonify({'status': 'stopped'})
    else:
        return jsonify({'status': 'unknown_action'})



if __name__ == '__main__':
    app.run(debug=True)
