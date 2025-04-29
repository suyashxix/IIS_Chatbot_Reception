# Project Title : Reception Chatbot with Multilingual Text and Voice support

## 1. Description/Objective: 
This project aims to build a Multilingual Reception Chatbot that supports both text based and voice based 
input according to the user's preference. The chatbot uses Natural Language Processing for intent identification,
LLMs for handling voice input, and MongoDB for secure data handling.

## 2. Necessary Libraries / Installation Requirements
Manually install the required libraries :
```bash
pip install pymongo cryptography spacy fpdf requests pyaudio openai-whisper numpy
```
After installing spacy, you also need to install :
```bash
python -m spacy download en_core_web_sm
```
If ollama is not available via pip and is a custom/internal package,make sure it's installed or accessible
via your environment.

## 3 Commands To Run the project
