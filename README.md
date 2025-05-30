# Project Title: Reception Chatbot with Multilingual Text and Voice Support

## 1. Description/Objective: 
This project aims to build a Multilingual Reception Chatbot that supports text-based and voice-based 
input according to the user's preference. The chatbot uses Natural Language Processing for intent identification, LLMs to handle voice input, and MongoDB for secure data handling.

## 2. Necessary Libraries / Installation Requirements
Install the required libraries by running:

```bash
pip install -r requirements.txt
```

Alternatively manually install the required libraries :
```bash
pip install pymongo cryptography spacy fpdf requests pyaudio openai-whisper numpy
```
After installing spacy, you also need to install :
```bash
python -m spacy download en_core_web_sm
```
If ollama is not available via pip and is a custom/internal package, make sure it's installed or accessible
via your environment.

## 3. Commands to Run the Project

# Step 1: Clone the repository
git clone https://github.com/suyashxix/IIS_Chatbot_Reception.git

# Step 2: Navigate into the project directory
cd IIS_Chatbot_Reception

# Step 3: Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Step 4: Run the chatbot
python chatbot.py
> ✅ **Note:** The `encryption_key.key` file is already included in the repository, so you do not need to generate it manually. Just ensure it remains in the root directory when running the script.

## File Structure
```
IIS_Chatbot_Reception
│
├── Chatbot_Reception_G04.py     # Main script to run the chatbot
├── Chatbot_Video_Demo.mp4       # Demo video (optional)
├── README.md                    # Setup instructions and project info
├── encryption_key.key           # Encryption key file
└── requirements.txt             # Python dependencies
```


