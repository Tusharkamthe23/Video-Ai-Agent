import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file, get_file
import google.generativeai as genai
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv
import os
import streamlit.components.v1 as components
# Load environment variables
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Streamlit page configuration
st.set_page_config(
    page_title="Multimodal AI Agent",
    page_icon="🤖",
    layout="wide"

)


st.title("📹 Multimodal AI Agent")
st.markdown(
    """
    Welcome to the **Multimodal AI Agent** powered  by **Gemini 2.0 Flash Exp**! 
    Use  this app to upload videos , ask questions, and get AI-generated insights.
    Navigate through the pages to learn more about the app.
    """
)

# Initialize the AI Agent
@st.cache_resource
def initialize_agent():
    return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,

    )

multimodal_Agent = initialize_agent()

# File uploader
video_file = st.file_uploader( 
     "📤 Upload a video file", type=['mp4', 'mov', 'avi'], help="Supported formats: MP4, MOV, AVI"
)

if video_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(video_file.read())
        video_path = temp_video.name

    # Embed video with custom width and height
    video_html = f"""
    <video width="480" height="270" controls>
        <source src="data:video/mp4;base64,{video_file.getvalue().hex()}" type="video/mp4">
        Your browser does not support the video tag.
    </video> 
    """
    st.markdown("### Video Preview")
    components.html(video_html, height=300)

    # User query input
    user_query = st.text_area(
        "🤔 What insights are you seeking from the video?",
        placeholder="E.g., ' Summarize the key moments'  or  ' Identifye key topics discussed'.",
        max_chars=300,
        help="Provide specific questions for better  results."

    )

    if st.button("🔍 Analyze Video"):
        if not user_query.strip():
            st.warning("⚠️ Please enter a question or insight to analyze the video.")
        else:
            try:
                with st.spinner("⏳ Processing video and gathering insights..."):
                    # Upload and process video file
                    processed_video = upload_file(video_path)
                    while processed_video.state.name == "PROCESSING":
                        time.sleep(1)

                        processed_video = get_file(processed_video.name)



                    # Generate prompt for analysis
                    analysis_prompt = (
                        f"""
                        Analyze the uploaded video for content and context.
                        Respond to the following query using video insights and supplementary web research:
                        {user_query}

                        Provide a detailed, user-friendly, and actionable response.
                        """
                    )



                    # AI agent processing
                    response = multimodal_Agent.run(analysis_prompt, videos=[processed_video])

                # Display the result
                st.subheader("📊 Analysis Result")
                st.markdown(response.content)

            except Exception as error:
                st.error(f"❌ An error occurred: {error}")
            finally:
                Path(video_path).unlink(missing_ok=True)
else:
    st.info("📥 Upload a video to start the analysis.")



# Footer
st.markdown(
    """
    ---
    Developed  by Tushar Kamthe
    Powered by **Phidata Multimodal AI Agent** 
    """,
    unsafe_allow_html=True
)
