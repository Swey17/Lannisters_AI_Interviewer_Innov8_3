import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import pickle
from pydub import AudioSegment


f = open('gemini_api.pkl', 'rb')
my_api_key = pickle.load(f)
f.close()
genai.configure(api_key=my_api_key)
model = genai.GenerativeModel('gemini-2.5-flash')
level = 2
remaining_questions = 3
ft = open('topics.bin', 'rb')
topics = pickle.load(ft)
ft.close()
score = []

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

def gemini_process_audio_and_text(prompt_text, audio_bytes, mime_type="audio/wav"):
    audio_file = {
        'mime_type': mime_type,
        'data': audio_bytes
    }
    try:
        response = model.generate_content([prompt_text, audio_file])
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

st.set_page_config(
    page_title="Lanister - AI Interviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Main chat container */
    .st-emotion-cache-1jicfl2 {
        padding-top: 2rem;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F0F2F6;
    }
    [data-testid="stSidebar"] h2 {
        color: #1E293B;
    }
    /* Chat messages */
    .stChatMessage {
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }
    /* Tall text area for code */
    textarea[data-baseweb="textarea"] {
        height: 500px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def text_to_speech(text):

    try:
        audio_fp = io.BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp.read()
    except Exception as e:
        st.error(f"Could not generate audio: {e}")
        return None

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello, Today we will do a mock interview.\nPlease Choose your preferred language"}]
if "code_content" not in st.session_state:
    st.session_state.code_content = ""

st.title("Lanister - AI Interviewer")
chat_col, code_col = st.columns(2)


st.sidebar.header("Code Editor")
code_col = st.sidebar.text_area(
    "Editable Code Panel",
    value=st.session_state.code_content,
    height=750,
    width=700,
    label_visibility="collapsed"
)

with chat_col:
    st.header("Chat")
    # Display all history messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            # Read aloud button
            if message["role"] == "assistant":
                audio_bytes = text_to_speech(message["content"])
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")

    st.markdown("---")
    st.markdown("#### Input by Speech")
    audio_info = mic_recorder(
        start_prompt="Speak 🎙️",
        stop_prompt="Recording... Stop ⏹️",
        key='speech_input'
    )

    prompt = st.chat_input("Respond here...")

# if audio_info and audio_info['bytes']:
#     st.info("Speech received. You would now transcribe this audio.")
#     prompt = "This is a placeholder for the transcribed speech."
#     st.warning("Speech-to-text is a placeholder. To implement it, you need to connect to a transcription service.")

def phraser(user_response):
    text = f"""You are an AI Tech Interviewer and Based on the History of responses
    You have to ask the next question from the list of topics.
    
    Topics are - {topics}

    ask user level {level} question.
]
    You have to ask a total of 10 independent questions from the above list.
    if the user is not able to answer then you can go to one level less.
    If the user is able to answer then you can go to level 3 and so on
    
    And This is the Code Window -
    '{st.session_state.code_content}'
    Based on the code and the history of responses, ask the next followup question and cross questions.
    History of responses: '{history}'

    This is the last response of user - '{user_response}'

    And If a Question is completely answered by the user then say strictly say -> 1
    If the user is  completely clueless (cannot answer in 3 tries or followups )then say strictly say -> give -1
    And if followup question is about to be asked then just ask the followup question and dont give any score.
    Response Must only contain One code block if any code is to be shared.
    Put normal text outside the code block.
    Strictly ask the user to write code , and avoid theoretical questions.
"""
    return text

history = [f"Preferred Language - {st.session_state.messages[0]['content']}"]

if prompt:
    # 1. Simulate an LLM response (THIS IS WHERE YOU'D CALL YOUR BACKEND)
    with st.spinner("Thinking..."):
        if audio_info and audio_info['bytes']:
            audio_wav = convert_webm_to_wav(audio_info['bytes'])
            user_final = gemini_process_audio_and_text(prompt_text="Just give its transcription", audio_bytes=audio_wav)
        else:
            user_final = prompt

        st.session_state.messages.append({"role": "user", "content": prompt})
        
        final_prompt = phraser(user_response=user_final)
        gemini_response_text = gemini_response(final_prompt)

        if gemini_response_text[0] == '1':
            if level==5:
                score.append(level*2)
            else:
                score.append(level*2)
                level += 1
            history = [f"Preferred Language - {st.session_state.messages[0]['content']}"]
        elif gemini_response_text[0] == '-1':
            if level==1:
                score.append(0)
            else:
                level -= 1
                score.append(0)
            history = [f"Preferred Language - {st.session_state.messages[0]['content']}"]

        else:
            response = gemini_response_text[0:gemini_response_text.find("```")]
            code = gemini_response_text[gemini_response_text.find("```")+3:gemini_response_text.rfind("```")]
            if code.strip():  
                st.session_state.code_content = code.strip()

            st.session_state.messages.append({"role": "assistant", "content": response})
            history.append({"role": "user", "content": user_final})
            history.append({"role": "assistant", "content": gemini_response_text})

        ##################################
        # else:
        #     st.session_state.messages.append({"role": "user", "content": prompt})
        #     final_prompt = phraser(user_response=prompt)
        #     gemini_response_text = gemini_response(final_prompt)
        #     response = gemini_response_text[0:gemini_response_text.find(";;;")]
        #     code = gemini_response_text[gemini_response_text.find(";;;")+3:gemini_response_text.rfind(";;;")]
        #     if code.strip():  
        #         st.session_state.code_content = f"\n# Q: {prompt}\n{code}\n"
        #     st.session_state.messages.append({"role": "assistant", "content": response})

        remaining_questions -= 1
        if remaining_questions <= 0:
            total_score = sum(score)
            st.session_state.messages.append({"role": "assistant", "content": f"Interview Over! Your total score is {total_score} out of {10*level*2}."})
            prompt = None  

        print(sum(score), level, remaining_questions)
    # Rerun the app to display the new messages and updated code
    st.rerun()


