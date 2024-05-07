
from flask import Flask, render_template, request, jsonify
import cv2
import pyaudio
import wave
import cv2
import os
import openai
import pyttsx3  # For text-to-speech
import json
from utils import get_completion

import openai
import json
import os
import datetime

# Get the current date

# Get the current date
from flask import Flask, render_template, request, jsonify
import openai
import os
import datetime

# Get the current date
current_date = datetime.datetime.now().date()

# Define the date after which the model should be set to "gpt-3.5-turbo"
target_date = datetime.date(2024, 6, 12)

# Set the model variable based on the current date
if current_date > target_date:
    llm_model = "gpt-3.5-turbo"
else:
    llm_model = "gpt-3.5-turbo-0301"

# Set your OpenAI API key
openai.api_key = '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'  # Replace with your OpenAI API key

# Define job descriptions with their corresponding PDF file paths


app = Flask(__name__)

# Define variables to control recording
recording_audio = False
recording_video = False
audio_filename = None
video_filename = None
video_writer = None
audio_stream = None
audio_frames = []

# Function to start and stop video recording
#def toggle_video_recording():
audio = pyaudio.PyAudio()



def toggle_audio_video_recording(username):
    global recording_audio, audio_stream, audio_frames,audio
    global recording_video, video_writer, video_filename, audio_filename
    print('video tester')
    recording_audio = True
    recording_video = True
    video_filename = f"{username}_video.avi"
    audio_filename = f"{username}_audio.wav"

    audio = pyaudio.PyAudio()
    audio_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    audio_frames = []

    video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

    cap = cv2.VideoCapture(0)  

    try:
        while recording_audio and recording_video:
            # Record audio
            data = audio_stream.read(1024)
            audio_frames.append(data)
            #print(audio_frames)

            # Record video
            ret, frame = cap.read()
            if not ret:
                print('Error: Video capture failed')
                break

            video_writer.write(frame)

            cv2.imshow('my_video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
            # Press 'q' to stop recording
                break
            # cv2.imshow('my_video',frame)
            #print(ret)
            #print(frame)

            # video_writer.write(frame)
    except:
        print('Recording has been stopped')

    

    video_writer.release()
    cap.release()
    

    audio_stream.stop_stream()
    audio_stream.close()
    audio.terminate()  
    
    with wave.open(audio_filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b''.join(audio_frames))
    cv2.destroyAllWindows()
# Stop and release resources


# Add more JDs for other job streams

# Initialize final_questions outside of the "Generate Questions" block


job_descriptions = {
    'Python': 'path_to_python.txt',
    'Data Scientist': 'path_to_datascientist.txt',
    'Backend Developer': 'path_to_backend-developer.txt'
}


def read_job_description_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading job description from file: {e}")
        return ""

def generate_questions(job_description, num_questions=10):
    questions = []

    if job_description in job_descriptions:
        file_path = job_descriptions[job_description]
        job_description_text = read_job_description_from_file(file_path)

        # Generate questions using OpenAI's GPT-3
        response = openai.ChatCompletion.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": f"Generate {num_questions} interview questions for a {job_description} based on the following job description:"},
                {"role": "user", "content": job_description_text}
            ]
        )

        generated_questions = response["choices"][0]["message"]["content"].split('\n')  # Split by '\n'
        questions.extend(generated_questions)  # Append to the list

    return questions

@app.route('/')
def index():
    return render_template('index_1.html', questions=[])

@app.route('/generate_questions', methods=['POST'])
def generate_questions_1():
    selected_job_stream = request.json.get('jobStream')
    generated_questions = generate_questions(selected_job_stream)
    generated_questions.remove('')
    print(generated_questions)

    
    return jsonify({'questions': generated_questions})



@app.route('/record', methods=['POST'])
def record():
    try:
        global recording_audio, recording_video, audio_frames, audio_filename, video_filename

        data = request.json
        print(data)
        try:

            if 'username' in data:
                username = data['username']
                print(username)


            if data['action'] == 'start':
                if not recording_audio and not recording_video:
                    try:
                        username = data['username']
                        toggle_audio_video_recording(username)
                        return jsonify({'status': 'started'})
                    except Exception as e:
                        print(f'Error starting recording: {e}')
                        return jsonify({'status': 'error', 'message': str(e)})
                else:
                    return jsonify({'status': 'already_started'})
            elif data['action'] == 'stop':
                global audio_frames, audio, audio_stream
                recording_audio = False
                recording_video = False
                print('Recording has been stopped')
                return jsonify({'status': 'stopped'})
            else:
                return jsonify({'status': 'unknown_action'})
        except:
            pass    
    except Exception as e:
        print(f'Error in recording: {e}')
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
