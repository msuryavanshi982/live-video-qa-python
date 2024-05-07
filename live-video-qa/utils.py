import azure.cognitiveservices.speech as speechsdk
import openai
SPEECH_KEY = '48b4c25e057f47438e58e45c48de4df2'
SPEECH_REGION = 'eastus'

def recognize_from_microphone(wavefile):
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language="en-IN"

    audio_config = speechsdk.audio.AudioConfig(filename=wavefile)
    # audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    # elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
    #     print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    # elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = speech_recognition_result.cancellation_details
    #     print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #         print("Error details: {}".format(cancellation_details.error_details))
    #         print("Did you set the speech resource key and region values?")

    return speech_recognition_result.text




def get_completion(message, model="gpt-3.5-turbo"):
    message = message[:4090] + "..." if len(message) > 4090 else message
    prompt = f"""
        Read the given job description carefully and generate top 5 questions with medium level and high level questions in a dictionary format

        don't give any questions that are not relevant to job descriptions

        {{"medium_level_questions":["set of questions are defined here"],
        "high_level_questions":["set of questions are defined here"]}}

        Review text: '''{message}'''
    """  
    
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]