import google.generativeai as genai
import pickle
from pydub import AudioSegment
import io

f = open('gemini_api.pkl', 'rb')
my_api_key = pickle.load(f)
f.close()
genai.configure(api_key=my_api_key)

# Use a model that explicitly supports audio, like the new 'gemini-2.5-flash'
model = genai.GenerativeModel('gemini-2.5-flash')

# --- Helper function to convert audio format ---
# The mic_recorder gives 'webm'. Gemini works best with 'wav' or 'mp3'.
def convert_webm_to_wav(webm_bytes):
    """Converts audio from webm bytes to wav bytes."""
    try:
        segment = AudioSegment.from_file(io.BytesIO(webm_bytes), format="webm")
        wav_io = io.BytesIO()
        segment.export(wav_io, format="wav")
        return wav_io.getvalue()
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

def gemini_response(prompt_text):

    response = model.generate_content(prompt_text)

    return response.text 


# --- NEW Function to Process Audio and Text ---
def gemini_process_audio_and_text(prompt_text, audio_bytes, mime_type="audio/wav"):
    """
    Sends both a text prompt and audio data to the Gemini model.
    """
    # 1. Prepare the audio data part for the API
    audio_file = {
        'mime_type': mime_type,
        'data': audio_bytes
    }

    # 2. Send both text and audio in a list to the model
    try:
        response = model.generate_content([prompt_text, audio_file])
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    # This is how you would use it if you had an audio file
    # For this example, we'll simulate a silent wav file
    # In your app, you will get the bytes from the mic_recorder
    
    # Example: Transcribe the audio
    prompt = "Please transcribe the following audio."

    print(gemini_response(prompt))