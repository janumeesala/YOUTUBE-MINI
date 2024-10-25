import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator
import re

# Load all the environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the base prompt for the generative AI model
base_prompt = """You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video 
and providing the important summary in points within 500 words. Please provide the summary of the text given here: """

def get_difficulty_prompt(difficulty):
    if difficulty == "Simple":
        return base_prompt + " Use simple language that is easy to understand."
    elif difficulty == "Medium":
        return base_prompt + " Use a moderate level of language complexity."
    elif difficulty == "Hard":
        return base_prompt + " Use advanced language and include technical terms if applicable."
    else:
        return base_prompt

def extract_video_id(youtube_video_url):
    """Extract the video ID from the YouTube video URL."""
    video_id = None
    if "youtube.com/watch?v=" in youtube_video_url:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in youtube_video_url:
        video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
    return video_id

def extract_transcript_details(video_id):
    """Extract the transcript from the YouTube video."""
    try:
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        st.error(f"An error occurred while fetching the transcript: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    """Generate summary using Google's generative AI model."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

def translate_text(text, target_language):
    """Translate the given text to the target language."""
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Set page configuration
st.set_page_config(page_title="YouTube Transcript Converter", page_icon="📹", layout="centered", initial_sidebar_state="auto")

# Inject CSS to add a background image
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://www.example.com/your-image.jpg');
        background-size: cover;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        
        # Language selection for translation
        languages = {"English": "en","Spanish": "es","French": "fr","German": "de","Chinese": "zh-cn","Japanese": "ja","Korean": "ko","Hindi": "hi","Urdu": "ur","Telugu": "te","Kannada": "kn",}
        target_language = st.selectbox("Select the target language for the summary:", list(languages.keys()))

        # Difficulty selection for the summary
        difficulty_levels = ["Simple", "Medium", "Hard"]
        difficulty = st.selectbox("Select the difficulty level of the summary:", difficulty_levels)

        if st.button("Get Summary Notes"):
            transcript_text = extract_transcript_details(video_id)

            if transcript_text:
                with st.spinner("Processing summary... Please wait."):
                    # Generate the summary with the selected difficulty level
                    prompt = get_difficulty_prompt(difficulty)
                    summary = generate_gemini_content(transcript_text, prompt)
                
                if summary:
                    # Translate the summary to the selected language
                    translated_summary = translate_text(summary, languages[target_language])

                    st.markdown("## Summarized Notes:")
                    st.write(translated_summary)

                    st.download_button(
                        label="Download Summary",
                        data=translated_summary,
                        file_name="summary.txt",
                        mime="text/plain"
                    )
    else:
        st.error("Invalid YouTube URL.")
