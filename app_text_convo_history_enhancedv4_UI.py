import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import pandas as pd
import base64
from googletrans import Translator

# Set page configuration
st.set_page_config(page_title="Koustav's GenX Engine", page_icon=":robot:", layout="wide")

# Load environment variables
load_dotenv()

# Initialize translator
translator = Translator()

# Custom CSS for styling
def add_custom_css():
    st.markdown("""
        <style>
        /* Space theme background */
        .stApp {
            background: url('https://wallpaperaccess.com/full/4379622.jpg');
            background-size: cover;
            color: #ffffff;
        }

        /* Header styling */
        header {
            background: rgba(20, 20, 20, 0.6);
            padding: 10px;
            border-radius: 10px;
            color: white;
        }

        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: rgba(30, 30, 30, 0.4);
            color: #ffffff;
        }

        /* Input and buttons styling */
        .stTextInput > div > div > input {
            background: rgba(30, 30, 30, 0.6);
            color: #ffffff;
            border-radius: 10px;
        }

        .stButton > button {
            background: #0078D4;
            color: #ffffff;
            border: None;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .stButton > button:hover {
            background: #005a9e;
        }

        /* Predefined questions select box */
        .stSelectbox > div > div {
            background: rgba(30, 30, 30, 0.4);
            color: #ffffff;
            border-radius: 10px;
        }

        /* Conversation history section */
        .stContainer {
            background: rgba(30, 30, 30, 0.4);
            border-radius: 10px;
            padding: 20px;
        }

        /* Download links */
        a.download-link {
            color: #ffcc00;
            text-decoration: None;
        }

        a.download-link:hover {
            text-decoration: underline;
        }

        /* General text color and headings */
        h1, h2, h3, h4, h5, h6 {
            color: white;
        }

        /* Custom subheading styles */
        .subheading {
            color: white;
        }
        
        /* Answer text color */
        .answer-text {
            color: black !important;
        }

        /* Info message color */
        .info-message {
            color: #ffcc00;
        }
        </style>
        """, unsafe_allow_html=True)

# Function to return the response
def load_answer(question, conversation_history, target_language):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    
    # Include the conversation history in the context
    context = "\n".join(conversation_history) + f"\nUser: {question}\nAI:"
    
    answer = llm.invoke(context).content
    
    # Translate answer to target language
    if target_language != 'en':
        answer = translator.translate(answer, dest=target_language).text
    
    return answer

# Function to clear conversation history
def clear_history():
    st.session_state.conversation_history = []

# Function to download conversation history as text file
def download_history_text():
    history_str = "\n".join(st.session_state.conversation_history)
    b64 = base64.b64encode(history_str.encode()).decode()
    href = f'<a class="download-link" href="data:text/plain;base64,{b64}" download="conversation_history.txt">Download conversation history (TXT)</a>'
    st.markdown(href, unsafe_allow_html=True)

# Function to download conversation history as CSV file
def download_history_csv():
    history_df = pd.DataFrame(st.session_state.conversation_history, columns=["Conversation"])
    csv = history_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a class="download-link" href="data:file/csv;base64,{b64}" download="conversation_history.csv">Download conversation history (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)

# Initialize the session state to store the conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Predefined questions
predefined_questions = [
    "Tell me about the Taj Mahal.",
    "What is the capital of France?",
    "Explain the theory of relativity.",
    "What are the benefits of a healthy diet?",
    "How does a computer work?"
]

# Add custom CSS for styling
add_custom_css()

# App UI starts here
st.header("GenX Engine Pro")

# Sidebar for navigation
tab = st.sidebar.selectbox("Choose a section", ["Chat", "Conversation History"], key="section")

# Language selection
languages = {'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Chinese': 'zh-cn', 'Hindi': 'hi'}
language = st.sidebar.selectbox("Select Language", list(languages.keys()))
target_language = languages[language]

# Chat section
if tab == "Chat":
    # Function to get text input
    def get_text():
        input_text = st.text_input("You: ", key="input", on_change=reset_predefined_question)
        return input_text

    # Function to reset predefined question
    def reset_predefined_question():
        st.session_state.predefined_question = ""

    # Initialize predefined_question in session state
    if 'predefined_question' not in st.session_state:
        st.session_state.predefined_question = ""

    user_input = get_text()
    predefined_question = st.selectbox("Or select a predefined question:", [""] + predefined_questions, key="predefined_question")
    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.button('Generate')
    with col2:
        clear = st.button('Clear History')

    # If clear history button is clicked
    if clear:
        clear_history()

    # If generate button is clicked
    if submit and (user_input or predefined_question):
        # Use the predefined question if available
        question = predefined_question if predefined_question else user_input
        
        # Translate question to English if necessary
        if target_language != 'en':
            question = translator.translate(question, dest='en').text
        
        # Get the previous conversation history
        conversation_history = st.session_state.conversation_history
        
        # Generate response based on the current question and conversation history
        response = load_answer(question, conversation_history, target_language)
        
        # Update the conversation history
        conversation_history.append(f"User: {question}")
        conversation_history.append(f"AI: {response}")
        
        # Save the updated conversation history in session state
        st.session_state.conversation_history = conversation_history
        
        # Display the latest response
        st.subheader("Answer:")
        st.markdown(f'<div class="answer-text">{response}</div>', unsafe_allow_html=True)

    # Display a message if there is no input
    if not user_input and not predefined_question and submit:
        st.error("Please enter a question or select a predefined question.")

# Conversation History section
elif tab == "Conversation History":
    st.subheader("Conversation History")
    conversation_history = st.session_state.conversation_history
    
    if conversation_history:
        for i in range(0, len(conversation_history), 2):
            st.text(f"{conversation_history[i]}")
            st.text(f"{conversation_history[i+1]}")
        st.markdown("---")
        download_history_text()
        download_history_csv()
    else:
        st.info("No conversation history yet.")

# Apply custom styles to specific elements
st.markdown(
    """
    <style>
    .subheading {
        color: white !important;
    }
    .download-link {
        color: #ffcc00 !important;
    }
    .info-message {
        color: #ffcc00 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Setting the subheadings color directly
st.markdown('<p class="subheading">You:</p>', unsafe_allow_html=True)
st.markdown('<p class="subheading">Or select a predefined question:</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p class="subheading">Choose a section</p>', unsafe_allow_html=True)
