import time as t
import os
# Set the correct path for MongoCrypt
os.environ["LIBMONGOCRYPT_PATH"] = r"C:\Users\Suyash\Programming\Project_IIS\venv\Lib\site-packages\pymongocrypt\mongocrypt.dll"

KEY_FILE="encryption_key.key"

import spacy
nlp = spacy.load("en_core_web_sm")

import json
import re
import requests
from fpdf import FPDF

import ollama
from pprint import pprint


import urllib.parse
from bson.codec_options import CodecOptions
from bson.binary import STANDARD

import pymongo
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


import requests
import base64
import pyaudio
import wave
import whisper
import numpy as np
audio = pyaudio.PyAudio()
default_device_index = audio.get_default_input_device_info()["index"]
print(f"Using Input Device Index: {default_device_index}")


def record_audio(filename="temp_audio.wav", duration=5, samplerate=44100, device_index=None):
    print("Recording... Please speak now.")
    stream = audio.open(format=pyaudio.paInt16, 
                        channels=1, 
                        rate=samplerate, 
                        input=True, 
                        frames_per_buffer=1024,
                        input_device_index=device_index or default_device_index)

    frames = []
    for _ in range(0, int(samplerate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    # Save the recording
    wf = wave.open(filename, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(samplerate)
    wf.writeframes(b"".join(frames))
    wf.close()

    print("Recording complete.")

# Function for converting base64 string to wav output file (used in text to speech function)
def base64_to_wav(base64_string, output_file):
    try:
        if not base64_string:
            print("❌ Critical Chatbot Failiure*(Empty base64 string) Exiting....")
            return
        wav_data = base64.b64decode(base64_string)
        with open(output_file, 'wb') as f:
            f.write(wav_data)
    except Exception as e:
        print(f'Error converting base64 to .wav: {e}')
    
'''
make language choose in following form
1 - English
2 - Hindi
3 - Bengali
4 - Gujarati
5 - Kannada
6 - Malayalam
7 - Marathi
8 - Odia
9 - Punjabi
10 - Tamil
11 - Telugu
Enter number corresponding to language:
'''
def language(lang_name):
    match lang_name:
        case 2:
            return "hi-IN"
        case 3:
            return "bn-IN"
        case 4:
            return "gu-IN"
        case 5:
            return "kn-IN"
        case 6:
            return "ml-IN"
        case 7:
            return "mr-IN"
        case 8:
            return "od-IN"
        case 9:
            return "pa-IN"
        case 10:
            return "ta-IN"
        case 11:
            return "te-IN"
        case _:
            return "en-IN"

# Translate function to convert Chatbot text to desired language
def translate(text, source_lang_num, target_lang_num, gender):
    if (source_lang_num==target_lang_num):
       return text
    url = "https://api.sarvam.ai/translate"
    payload = {
        "input": text,
        "source_language_code": language(source_lang_num),
        "target_language_code": language(target_lang_num),
        "speaker_gender": gender,
        "mode": "formal",
        "model": "mayura:v1",
        "enable_preprocessing": False,
        "numerals_format": "international",
        "output_script": "fully-native"
    }
    headers = {
        "api-subscription-key": "b65a665d-aa1b-48ad-a421-53d9a77bf23d",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("translated_text", "Translation not available")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return f"Error: {response.status_code} - {response.text}"
    
# Speech to text + translate to convert user audio into english text which Chatbot can process
def stt_translate(audio):
    url = "https://api.sarvam.ai/speech-to-text-translate"

    payload = {'model': 'saaras:v1',
    'prompt': ''}
    path="C:\\Users\\Suyash\\Programming\\Project_IIS\\"

    files=[
    ('file',(audio,open(path+audio,'rb'),'audio/wav'))
    ]
    headers = {
    'api-subscription-key': "b65a665d-aa1b-48ad-a421-53d9a77bf23d"
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        translated_text = response.json().get("transcript", "Translation not available")
        return translated_text
    else:
        error="Error:"+ str(response.status_code)
        return error

# Text to speech to give Chatbot translate output to user
def tts(text,lang_name):
    import requests

    url = "https://api.sarvam.ai/text-to-speech"
    payload = {
        "inputs": [text],
        "target_language_code": language(lang_name),
        "speaker": "meera",
        "pitch": 1,
        "pace": 1,
        "loudness": 1.55,
        "speech_sample_rate": 8000,
        "enable_preprocessing": False,
        "model": "bulbul:v1"
    }
    headers = {
        "Content-Type": "application/json",
        'api-subscription-key': "b65a665d-aa1b-48ad-a421-53d9a77bf23d"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        audio = response.json().get("audios", "Translation not available")
        if(type(audio)==type([])):
            audio=audio[0]
        base64_to_wav(audio,"output.wav")
        return audio
    else:
        error="Error:"+ str(response.status_code)

def play_audio(filename):
    wf = wave.open(filename, 'rb')
    stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    stream.stop_stream()
    stream.close()
    wf.close()

faculty_names = [
  ("A V Subramanyam", "M", "Subramanyam", "Research and Development Block", "B-604"),
    ("Aasim Khan", "M", "Khan", "Research and Development Block", "B-202"),
    ("Abhijit Mitra", "M", "Mitra", "Research and Development Block", "A-605"),
    ("Anand Srivastava", "M", "Srivastava", "Research and Development Block", "Dont have location"),
    ("Angshul Majumdar", "M", "Majumdar", "Research and Development Block", "A-606"),
    ("Anmol Srivastava", "M", "Srivastava", "Research and Development Block", "A-404"),
    ("Anubha Gupta", "F", "Gupta", "Research and Development Block", "B-609"),
    ("Anuj Grover", "M", "Grover", "Research and Development Block", "A-610"),
    ("Anuradha Sharma", "F", "Sharma", "Research and Development Block", "B-311"),
    ("Arani Bhattacharya", "M", "Bhattacharya", "Research and Development Block", "B-510"),
    ("Arjun Ray", "M", "Ray", "Research and Development Block", "A-310"),
    ("Arun Balaji Buduru", "M", "Buduru", "Research and Development Block", "B-504"),
    ("Ashish Kumar Pandey", "M", "Pandey", "Research and Development Block", "B-307"),
    ("Bapi Chatterjee", "M", "Chatterjee", "Research and Development Block", "B-402"),
    ("Chanekar Prasad Vilas", "M", "Vilas", "Research and Development Block", "B-610"),
    ("Debajyoti Bera", "M", "Bera", "Research and Development Block", "B-508"),
    ("Debarka Sengupta", "M", "Sengupta", "Research and Development Block", "A-306"),
    ("Debidas Kundu", "M", "Kundu", "Research and Development Block", "A-606"),
    ("Debika Banerjee", "F", "Banerjee", "Research and Development Block", "B-310"),
    ("Deepak Prince", "M", "Prince", "Research and Development Block", "A-210"),
    ("Dhruv Kumar", "M", "Kumar", "Research and Development Block", "A-506"),
    ("Diptapriyo Majumdar", "M", "Majumdar", "Research and Development Block", "B-501"),
    ("G.P.S. Raghava", "M", "Raghava", "Research and Development Block", "A-302"),
    ("Ganesh Bagler", "M", "Bagler", "Research and Development Block", "A-305"),
    ("Gaurav Ahuja", "M", "Ahuja", "Research and Development Block", "A-303"),
    ("Gaurav Arora", "M", "Arora", "Research and Development Block", "B-206"),
    ("Gautam Shroff", "M", "Shroff", "Research and Development Block", "A-510"),
    ("Gayatri Nair", "F", "Nair", "Research and Development Block", "B-212"),
    ("J. V. Meenakshi", "F", "Meenakshi", "Research and Development Block", "B-205"),
    ("Jainendra Shukla", "M", "Shukla", "Research and Development Block", "A-410"),
    ("Jaspreet Kaur Dhanjal", "F", "Dhanjal", "Research and Development Block", "A-307"),
    ("Kalpana Shankhwar", "F", "Shankhwar", "Research and Development Block", "A-403"),
    ("Kaushik Kalyanaraman", "M", "Kalyanaraman", "Research and Development Block", "B-302"),
    ("Kiriti Kanjilal", "M", "Kanjilal", "Research and Development Block", "B-208"),
    ("Koteswar Rao Jerripothula", "M", "Jerripothula", "Research and Development Block", "B-405"),
    ("Manohar Kumar", "M", "Kumar", "Research and Development Block", "B-207"),
    ("Manuj Mukherjee", "M", "Mukherjee", "Research and Development Block", "A-608"),
    ("Md. Shad Akhtar", "M", "Akhtar", "Research and Development Block", "B-406"),
    ("Monika Arora", "F", "Arora", "Research and Development Block", "A-304"),
    ("Mrinmoy Chakrabarty", "M", "Chakrabarty", "Research and Development Block", "A-202"),
    ("Mukesh Mohania", "M", "Mohania", "Research and Development Block", "A-507"),
    ("Mukulika Maity", "F", "Maity", "Research and Development Block", "B-509"),
    ("N. Arul Murugan", "M", "Murugan", "Research and Development Block", "A-311"),
    ("Nabanita Ray", "F", "Ray", "Research and Development Block", "B-312"),
    ("Nikhil Gupta", "M", "Gupta", "Research and Development Block", "B-511"),
    ("Nishad Patnaik", "M", "Patnaik", "Research and Development Block", "A-205"),
    ("Ojaswa Sharma", "M", "Sharma", "Research and Development Block", "A-511"),
    ("Pankaj Jalote", "M", "Jalote", "Research and Development Block", "A-705"),
    ("Paro Mishra", "F", "Mishra", "Research and Development Block", "B-209"),
    ("Piyus Kedia", "M", "Kedia", "Research and Development Block", "B-505"),
    ("Pragma Kar", "F", "Kar", "Research and Development Block", "A-411"),
    ("Pragya Kosta", "F", "Kosta", "Research and Development Block", "B-607"),
    ("Prahllad Deb", "M", "Deb", "Research and Development Block", "B-305"),
    ("Praveen Priyadarshi", "M", "Priyadarshi", "Research and Development Block", "A-203"),
    ("Pravesh Biyani", "M", "Biyani", "Research and Development Block", "A-604"),
    ("Pushpendra Singh", "M", "Singh", "Research and Development Block", "A-502"),
    ("Rajiv Raman", "M", "Raman", "Research and Development Block", "B-507"),
    ("Rajiv Ratn Shah", "M", "Shah", "Research and Development Block", "A-409"),
    ("Ram Krishna Ghosh", "M", "Ghosh", "Research and Development Block", "B-601"),
    ("Ranjan Bose", "M", "Bose", "Research and Development Block", "A-707"),
    ("Ranjitha Prasad", "F", "Prasad", "Research and Development Block", "A-403"),
    ("Ravi Anand", "M", "Anand", "Research and Development Block", "A-503"),
    ("Richa Gupta", "F", "Gupta", "Research and Development Block", "A-406"),
    ("Rinku Shah", "M", "Shah", "Research and Development Block", "B-502"),
    ("Ruhi Sonal", "F", "Sonal", "Research and Development Block", "A-211"),
    ("Saket Anand", "M", "Anand", "Research and Development Block", "B-410"),
    ("Sambuddho", "M", "Sambuddho", "Research and Development Block", "B-503"),
    ("Sanat K Biswas", "M", "Biswas", "Research and Development Block", "B-602"),
    ("Sanjit Krishnan Kaul", "M", "Kaul", "Research and Development Block", "B-411"),
    ("Sankha S Basu", "M", "Basu", "Research and Development Block", "B-306"),
    ("Sarthok Sircar", "M", "Sircar", "Research and Development Block", "B-303"),
    ("Satish Kumar Pandey", "M", "Pandey", "Research and Development Block", "A-206"),
    ("Sayak Bhattacharya", "M", "Bhattacharya", "Research and Development Block", "B-603"),
    ("Sayan Basu Roy", "M", "Roy", "Research and Development Block", "A-603"),
    ("Shamik Sarkar", "M", "Sarkar", "Research and Development Block", "B-412"),
    ("Shobha Sundar Ram", "F", "Ram", "Research and Development Block", "B-606"),
    ("Smriti Singh", "F", "Singh", "Research and Development Block", "B-211"),
    ("Sneh Saurabh", "M", "Saurabh", "Research and Development Block", "B-608"),
    ("Sneha Chaubey", "F", "Chaubey", "Research and Development Block", "B-308"),
    ("Soibam Haripriya", "F", "Haripriya", "Research and Development Block", "A-204"),
    ("Sonal Keshwani", "F", "Keshwani", "Research and Development Block", "A-405"),
    ("Sonia Baloni Ray", "F", "Ray", "Research and Development Block", "B-210"),
    ("Souvik Dutta", "M", "Dutta", "Research and Development Block", "B-203"),
    ("Sriram K", "M", "K", "Research and Development Block", "A-308"),
    ("Subhashree Mohapatra", "F", "Mohapatra", "Research and Development Block", "A-309"),
    ("Sujay Deb", "M", "Deb", "Research and Development Block", "A-607"),
    ("Sumit J Darak", "M", "Darak", "Research and Development Block", "B-605"),
    ("Supratim Shit", "M", "Shit", "Research and Development Block", "B-512"),
    ("Syamantak Das", "M", "Das", "Research and Development Block", "-505,"),
    ("Tanmoy Kundu", "M", "Kundu", "Research and Development Block", "A-512"),
    ("Tarini Shankar Ghosh", "M", "Ghosh", "Research and Development Block", "A-312"),
    ("Tavpritesh Sethi", "M", "Sethi", "Research and Development Block", "A-309"),
    ("V. Raghava Mutharaju", "M", "Mutharaju", "Research and Development Block", "B-404"),
    ("Venkata Ratnadeep Suri", "M", "Suri", "Research and Development Block", "B-204"),
    ("Vibhor Kumar", "M", "Kumar", "Research and Development Block", "A-304"),
    ("Vikram Goyal", "M", "Goyal", "Research and Development Block", "A-508"),
    ("Vinayak Abrol", "M", "Abrol", "Research and Development Block", "B-409"),
    ("Vivek Bohara", "M", "Bohara", "Research and Development Block", "A-609"),
    ("Vivek Kumar", "M", "Kumar", "Research and Development Block", "B-506"),
]
directions={
    "Old Academic Building":"Go straight, take a right at the next T-Point and then go straight until the next T point, the academic block will be to your left hand side",
    "Sports Complex": "Go straight and, when you see the football ground area, take a left , the Sports Block will be to your left.",
    "Lecture Hall Complex":" Go straight, take a right at the first intersection and keep going until the road starts top curve, stop and the Lecture Hall will be to your left.",
    "Research and Development Block":"Go straight and then take a right at the first intersection, keep going straight until the T point and then take a leftkeep going straight and R&D will be in front of you.",
    "Library Block":"Go straight and then take a right at the first intersection, keep going straight until the T point and then take a left. Keep going straight until you see some stairs on your left, take those stairs and the library will be in front of you.",
    "Hostel Block":"Go straight until the T-point, take a left and keep going straight until you hit another T-point and take another left, you will find the hostel buildings to your left",
    "Mess Block":"Go straight, take a right and you will find the mess block on your left."
    }

# Detects professors name in user's input
def prof_detect(user_input,faculty_names,collect,unique):
  name=[]
  for i in range(len(user_input)):
    if user_input[i] in collect:
      if(i!=0):
        if(user_input[i-1] not in collect):
          name.append([])
      else:
        name.append([])
      name[-1].append(user_input[i])
      # Collects consecutive words that are present in hashmap and combines them
  for i in range(len(name)):
    name[i]=" ".join(name[i])
    if(name[i] in prof):
      return prof[name[i]]
  # If professor's name is found it will return information relating to it, otherwise it will return nothing
  return []

prof={}
collect=set()
unique={}
dummy_room="A-410"
dummy_building="Research and Development Block"
temp=""
for i in faculty_names:
  temp=i[0].lower()
  prof[temp]=[i[1],i[2],i[3],i[4],[[],[],[],[],[]]]
  temp=temp.split()
  for j in temp:
    collect.add(j)
  if(temp[-1] not in unique):
    unique[temp[-1]]=[" ".join(temp)]
  else:
    unique[temp[-1]].append(" ".join(temp))

def generate_summarized_report(dialogue, model='deepseek-r1:7b', temperature=0.8):
    convo = "Summarize this dialogue/conversation between a chatbot and a user. Use plain language.\nData:\n"
    convo+="\n".join(dialogue)
    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': convo}],
        options={'temperature': temperature}
    )
    # Clean up response
    full_response = response['message']['content']
    return full_response.split('</think>')[-1].strip() if '</think>' in full_response else full_response.strip()
generate_summarized_report(["skibidy","hello"])

# Getting name of the user
def name(str,collect):
  new_str = scrubber.clean(str)
  new_ln = len(new_str)
  name_list = []
  temp_list = new_str.split("{{NAME}}")
  ind = new_str.find("{")
  temp_str = str[ind:]
  for i in temp_list[1:]:
    if i in ["",","]:
      name_list.append(temp_str)
      continue
    end = temp_str.find(i)
    name_list.append(temp_str[:end])
    temp_str = temp_str[end+len(i):]
  end = (new_str[::-1]).find("}")
  ln = len(str)
  if(name_list !=[]):
    for i in name_list:
      if i not in collect:
        return ", "+i
  return ""

def gender_find(str):
  if str=="M":
    return "Mr."
  elif str=="F":
    return "Ms."

def location(user_input,directions):
  acad={"admission","admissions","academic"}
  sport={"sport","guesthouse","table-tennis","billiards","sports"}
  lhc={"lecture","hall","lectures","auditorium"}
  lib={"library","books"}
  rnd={"research","development","lab","labs","rnd"}
  hstl={"hostel","hostels"}
  mess={"mess","food"}
  for i in user_input:
    if i in acad:
      return (i,"Old Academic Building")
    if i in sport:
      return (i,"Sports Complex")
    if i in lhc:
      return (i,"Lecture Hall Complex")
    if i in rnd:
      return (i,"Research and Development Block")
    if i in lib:
      return (i,"Library Block")
    if i in hstl:
      return (i,"Hostel Block")
    if i in mess:
      return (i,"Mess Block")
  return ""

def generate_report(cust_details, meeting_data,comments, action, filename="customer_report_ttt.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Times", style='B', size=18)
    pdf.cell(200, 10, "RECEPTION SERVICE REPORT", ln=True, align='C')
    pdf.ln(10)

    # Customer Details Section
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, "Customer Details", ln=True, border='B')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    # Create a table for customer details
    col_width = 95
    row_height = 10
    for key, value in cust_details.items():
        pdf.cell(col_width, row_height, key, border=1)
        pdf.cell(col_width, row_height, str(value), border=1, ln=True)
    pdf.ln(10)

    # Meetings Summary Section
    pdf.set_font("Times", style='B', size=14)
    pdf.cell(200, 10, "Meeting(s)", ln=True, border='B')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    # Define column widths for the symptoms table
    col_widths = [50,50, 40, 50]
    headers = ["Time Slot", "Room/Location", "Date", "Person Of Interest"]
    row_height = 10

    # Add table headers
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], row_height, header, border=1, align='C')
    pdf.ln(row_height)

    # Add symptom data rows
    # Add symptom data rows
    for entry in meeting_data:
        pdf.cell(col_widths[0], row_height, entry["time"], border=1)
        pdf.cell(col_widths[1], row_height, entry["location"], border=1)
        pdf.cell(col_widths[2], row_height, entry["date"], border=1)
        pdf.cell(col_widths[3], row_height, entry["poi"], border=1, ln=True)

    pdf.ln(5)
    pdf.set_font("Times", style='B', size=14)
    pdf.cell(200, 10, "Requested Services", ln=True, border='B')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    pdf.multi_cell(0, 10, action, border=0)
    pdf.ln(2)

    pdf.set_font("Times", style='B', size=14)
    pdf.cell(200, 10, "Additional Comments", ln=True, border='B')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    for i, comment in enumerate(comments, start=1):
        pdf.multi_cell(0, 10, f"{i}. {comment}", border=0)
        pdf.ln(2)

    # Save the PDF
    pdf.output(filename)
    print(f"Customer report successfully saved as {filename}.")


def meet_bool(user_input):
  doc = nlp(user_input)
  lemmatise=[token.lemma_.lower() for token in doc]
  for i in lemmatise:
    if i in ["meet","meeting","appointment"]:
      return True
  return False

def action(user_input):
  doc = nlp(user_input)
  lemmatise=doc.copy()
  for i in lemmatise:
    if i.pos_=="VERB":
      if i.lemma_.lower() in ["schedule","book","arrange"]:
        return 1
      elif i.lemma_.lower() in ["reschedule","move","shift"]:
        return 2
      elif i.lemma_.lower() in ["cancel","remove","suspend","postpone"]:
        return 3
  return 0

def add_day(random_day):
  if random_day.lower() in ["tuesday","tue"]:
    return 1
  elif random_day.lower() in [ "wednesday","wed"]:
    return 2
  elif random_day.lower() in ["thursday","thurs"]:
    return 3
  elif random_day.lower() in ["friday","fri"]:
    return 4
  return 0

def reverse_day(random_day):
  if random_day==0:
    return "Monday"
  elif random_day==1:
    return "Tuesday"
  elif random_day==2:
    return "Wednesday"
  elif random_day==3:
    return "Thursday"
  elif random_day==4:
    return "Friday"

def book_appointment(poi,name,day,time):
  if poi.lower() not in prof:
    return 1
  start=time
  end=time.copy()
  end[1]+=30
  if end[1]>=60:
    end[1]-=60
    end[0]+=1
  frame=[start,end]
  schedule=prof[poi.lower()][4][day]
  for i in range(len(schedule)):
    if (schedule[i][0]<frame[0] and schedule[i][1]>frame[0]) or (schedule[i][0]<frame[1] and schedule[i][1]>frame[1]) or (schedule[i][0]==frame[0] and schedule[i][1]==frame[1]):
      return 2
  frame.append(name)
  prof[poi.lower()][4][day].append(frame)
  return 0

def reschedule_appointment(poi,name):
  if poi.lower() not in prof:
    return 1
  schedule=prof[poi.lower()][4]
  for i in range(len(schedule)):
    for j in range(len(schedule[i])):
      if schedule[i][j][2]==name:
        ans=[schedule[i][j][0],reverse_day(i)]
        schedule[i].remove(schedule[i][j])
        return ans
  return 2

def check_appointment(poi,name,day,time):
  start=time
  end=time.copy()
  end[1]+=30
  if end[1]>=60:
    end[1]-=60
    end[0]+=1
  frame=[start,end]
  schedule=prof[poi.lower()][4][day]
  for i in range(len(schedule)):
    if schedule[i][0]==frame[0] and schedule[i][1]==frame[1] and schedule[i][2]==name:
      return 0
  return 2

def delete_appointment(poi,name,day,time):
  start=time
  end=time.copy()
  end[1]+=30
  if end[1]>=60:
    end[1]-=60
    end[0]+=1
  frame=[start,end]
  schedule=prof[poi.lower()][4][day]
  for i in range(len(schedule)):
    if schedule[i][0]==frame[0] and schedule[i][1]==frame[1] and schedule[i][2]==name:
      frame.append(name)
      schedule.remove(frame)
      return 0
  return 2


import os
import urllib.parse
from bson.codec_options import CodecOptions
from bson.binary import STANDARD

import pymongo
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from cryptography.fernet import Fernet

# Generate and save the encryption key
def load_or_generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print("New Encryption Key Generated! Store it securely.")
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    
    return key

key = load_or_generate_key()

print("Encryption Key:", key.decode())  # Save this key securely

import pymongo

cipher = Fernet(key)


def encrypt_data(plain_text):
    return cipher.encrypt(plain_text.encode()).decode()
def decrypt_data(encrypted_text):
    return cipher.decrypt(encrypted_text.encode()).decode()
client = pymongo.MongoClient("mongodb+srv://suyash:skt251271@projectclus.z3tkq.mongodb.net/?appName=ProjectClus")
db = client["secure_database"]
collection = db["customers"] 


# Function for calculating difference in time in a specfic format
def diff(a,b):
  ans=[0,0]
  ans[1]=b[1]-a[1]
  ans[0]=b[0]-a[0]
  if(ans[1]<0):
    ans[0]-=1
    ans[1]+=60
  return ans

date=[10,2,2024]

def chatbot(lang_num,gender):
   while True:
    
    welcome_text = "Welcome. How can I be of service for you today?"
    instruction_text = "Kindly provide your name, purpose of visit and person of interest so that I may help effectively."

    translated_welcome = translate(welcome_text, source_lang_num=1, target_lang_num=lang_num, gender=gender)
    translated_instruction = translate(instruction_text, source_lang_num=1, target_lang_num=lang_num, gender=gender)

    print(f"Chatbot: {translated_welcome}")
    tts(translated_welcome, lang_num)
    play_audio("output.wav")
    t.sleep(1)

    print(f"Chatbot: {translated_instruction}")
    tts(translated_instruction, lang_num)
    play_audio("output.wav")
    t.sleep(1)


    mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

    if mode == 'speak':
        while True:
          record_audio("user_input.wav", duration=5)
          user_input = stt_translate("user_input.wav").strip()
          print(f"You (spoken → translated to English): {user_input}")
          c = input("Is the recording satisfactory? Y/N: ").strip()
          if c.lower() == 'y':
            break 
    else:
        while True:
          typed_input = input("You (in native language): ").strip()
          user_input = translate(typed_input, lang_num, 1, gender).strip()
          print(f"You (typed → translated to English): {user_input}")
          c = input("Is the translation satisfactory? Y/N: ").strip()
          if c.lower() == 'y':
              break


    conversation=[]
    conversation.append("Chatbot: Welcome. How can I be of service for you today ?")
    conversation.append("Chatbot: Kindly provide your name, purpose of visit and person of interest so that I may help effectively.")
    conversation.append("You: "+user_input)
    cust_details = {}
    meeting_data = []
    meeting_bool=meet_bool(user_input)
    temp=user_input
    user_input=user_input.lower()
    user_input=user_input.split()
    prof_bool=prof_detect(user_input,faculty_names,collect,unique)
    loc=location(user_input,directions)
    key_words = [(ent.text, ent.label_) for ent in nlp(temp).ents]
    if meeting_bool:
      verb=action(temp)
      if verb==1:
        poi=""
        name=""
        day=""
        time=""
        for i in key_words:
          if i[0].lower() in prof:
            poi=i[0]
            key_words.remove(i)
            break
        for i in key_words:
          if i[1]=="PERSON":
            name=i[0]
          if i[1]=="DATE":
            day=i[0]
          if i[1]=="TIME":
            time=i[0]
        if poi=="":
          conversation.append("Chatbot: Kindly provide name of person you want to meet")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          
          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                poi = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {poi}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                poi = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {poi}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+poi)
    
    
        if name=="":
          conversation.append("Chatbot: Kindly provide your name for verification")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          
          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                name = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {name}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                name = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {name}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+name)
        if day=="":
          conversation.append("Chatbot: Kindly provide day on which you wish to meet")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          
          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                day = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {day}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                day = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {day}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+day)
  
        if time=="":
          conversation.append("Chatbot: Kindly input the time at which you wish to meet the required person")
          translated_ = translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              extra_prompt = "Please say the time clearly"
              translated_ = translate(extra_prompt, source_lang_num=1, target_lang_num=lang_num, gender=gender)
              tts(translated_, lang_num)
              play_audio("output.wav")
              t.sleep(1)

              while True:
                  record_audio("user_input.wav", duration=5)
                  time = stt_translate("user_input.wav").strip()
                  print(f"You (spoken → translated to English): {time}")
                  c = input("Is the recording satisfactory? Y/N: ").strip()
                  if c.lower() == 'y':
                      break
          else:
              time = input("You: ").strip()

          conversation.append("You: "+time)
        day=add_day(day)
        time_str = time
        time=time.split()
        if len(time)>1:
          time[0]=time[0].split(":")
          time[0]=list(map(int,time[0]))
          if time[1].lower()=="pm" and time[0][0]!=12:
            time[0][0]+=12
          time=time[0]
        else:
          time=time[0]
          time=time.split(":")
          time=list(map(int,time))
        if(len(time)==0):
          time.append(0)
        add_bool=book_appointment(poi,name,day,time)
        if add_bool==1:
          conversation.append("Chatbot: Sorry, I was not able to find the required person in the database")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

        elif add_bool==2:
          conversation.append("Chatbot: Sorry, the person you mentioned is busy at that time")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
        else:
          conversation.append("Chatbot: Appointment has been successfully booked")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          cust_details["Customer Name"] = name
          meeting = {}
          meeting["poi"] = poi
          tdate = date.copy()
          tdate[0] += day
          tstr = [str(i) for i in tdate]
          meeting["date"] = "-".join(tstr)
          meeting["time"] = time_str
          meeting["location"] = prof[poi.lower()][3]
          meeting_data.append(meeting)
          # print(cust_details)
          # print(meeting_data)
          conversation.append("Chatbot: To further contact you about the meeting, kindly provide e-mail adress and phone number")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          email = input("You: Email - ").strip()
          conversation.append("You: Email - "+email)
          phone = input("You: Phone Number - ").strip()
          conversation.append("You: Phone Number - "+phone)
          cust_details["Phone Number"]=phone
          cust_details["Email"]=email

          generate_report(cust_details,meeting_data,conversation,"Scheduled a meeting")
      elif verb==2:
        poi=""
        name=""
        for i in key_words:
          if i[0].lower() in prof:
            poi=i[0]
            key_words.remove(i)
            break
        for i in key_words:
          if i[1]=="PERSON":
            name=i[0]
        if poi=="":
          conversation.append("Chatbot: Kindly provide name of person who's meeting is being rescheduled")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                poi = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {poi}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                poi = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {poi}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+poi)

        if name=="":
          conversation.append("Chatbot: Kindly provide your name for verification")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                name = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {name}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                name = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {name}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+name)

        risc_bool=reschedule_appointment(poi,name)
        if type(risc_bool)==type([]):
          timing=":".join(list(map(str,risc_bool[0])))
          conversation.append(f"Chatbot: You have a meeting with {poi} on {risc_bool[1]} at {timing} .")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          conversation.append("Chatbot: Kindly provide updated day and time for meeting")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          translated_= translate("Please Enter the Updated day. ", source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                day = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {day}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                day = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {day}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: Updated Day - "+day)

          translated_= translate("Please input the Updated time. ", source_lang_num=1, target_lang_num=lang_num, gender=gender)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              extra_prompt = "Please say the time clearly"
              translated_ = translate(extra_prompt, source_lang_num=1, target_lang_num=lang_num, gender=gender)
              tts(translated_, lang_num)
              play_audio("output.wav")
              t.sleep(1)

              while True:
                  record_audio("user_input.wav", duration=5)
                  time = stt_translate("user_input.wav").strip()
                  print(f"You (spoken → translated to English): {time}")
                  c = input("Is the recording satisfactory? Y/N: ").strip()
                  if c.lower() == 'y':
                      break
          else:
              time = input("You: ").strip()
          time_str = time
          conversation.append("You: Updated Time - "+time)

          if day!="":
            day=add_day(day)
          if time!="":
            time=time.split()
            if len(time)>1:
              time[0]=time[0].split(":")
              time[0]=list(map(int,time[0]))
              if time[1].lower()=="pm" and time[0][0]!=12:
                time[0][0]+=12
              time=time[0]
            else:
              time=time[0]
              time=time.split(":")
              time=list(map(int,time))
          if(len(time)==0):
            time.append(0)
          add_bool=book_appointment(poi,name,day,time)
          if add_bool==1:
            conversation.append("Chatbot: Sorry, I was not able to find the required person in the database")
            translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
            print(translated_)
            tts(translated_, lang_num)
            play_audio("output.wav")
            t.sleep(1)
          elif add_bool==2:
              conversation.append("Chatbot: Sorry, the person you mentioned is busy at that time")
              translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
              print(translated_)
              tts(translated_, lang_num)
              play_audio("output.wav")
              t.sleep(1)
          else:
              conversation.append("Chatbot: Appointment has been successfully rescheduled")
              translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
              print(translated_)
              tts(translated_, lang_num)
              play_audio("output.wav")
              t.sleep(1)

              cust_details["Customer Name"] = name
              meeting = {}
              meeting["poi"] = poi
              tdate = date.copy()
              tdate[0] += day
              tstr = [str(i) for i in tdate]
              meeting["date"] = "-".join(tstr)
              meeting["time"] = time_str
              meeting["location"] = prof[poi.lower()][3]
              meeting_data.append(meeting)
              conversation.append("Chatbot: To further contact you about the meeting, kindly provide e-mail adress and phone number")
              translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
              print(translated_)
              tts(translated_, lang_num)
              play_audio("output.wav")
              t.sleep(1)

              email = input("You: Email - ").strip()
              conversation.append("You: Email - "+email)
              phone = input("You: Phone Number - ").strip()
              conversation.append("You: Phone Number - "+phone)
              cust_details["Phone Number"]=phone
              cust_details["Email"]=email
              generate_report(cust_details,meeting_data,conversation,"Rescheduled a meeting")
        elif risc_bool==1:
          conversation.append("Chatbot: Sorry, I was not able to find the required person in the database")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
        elif risc_bool==2:
          conversation.append("Chatbot: Sorry, your meeting with that person is not in database")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
      elif verb==3:
        poi=""
        name=""
        day=""
        time=""
        for i in key_words:
          if i[0].lower() in prof:
            poi=i[0]
            key_words.remove(i)
            break
        for i in key_words:
          if i[1]=="PERSON":
            name=i[0]
          if i[1]=="DATE":
            day=i[0]
            print(day)
          if i[1]=="TIME":
            time=i[0]
        if poi=="":
          conversation.append("Chatbot: Kindly provide name of person whom you are cancelling meeting with")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                poi = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {poi}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                poi = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {poi}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+poi)
        if name=="":
          conversation.append("Chatbot: Kindly provide your name for verification")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                name = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {name}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                name = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {name}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+name)
        if day=="":
          conversation.append("Chatbot: Kindly provide day on which the meeting is")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                day = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {day}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                day = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {day}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+day)
        if time=="":
          conversation.append("Chatbot: Kindly provide time at which you were to meet the required person")
          translated_ = translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              extra_prompt = "Please say the time clearly."
              translated_ = translate(extra_prompt, source_lang_num=1, target_lang_num=lang_num, gender=gender)
              tts(translated_, lang_num)
              play_audio("output.wav")
              t.sleep(1)

              while True:
                  record_audio("user_input.wav", duration=5)
                  time = stt_translate("user_input.wav").strip()
                  print(f"You (spoken → translated to English): {time}")
                  c = input("Is the recording satisfactory? Y/N: ").strip()
                  if c.lower() == 'y':
                      break
          else:
              time = input("You: ").strip()

          conversation.append("You: "+time)
        day=add_day(day)
        time_str=time
        time=time.split()
        if len(time)>1:
          time[0]=time[0].split(":")
          time[0]=list(map(int,time[0]))
          if time[1].lower()=="pm" and time[0][0]!=12:
            time[0][0]+=12
          time=time[0]
        else:
          time=time[0]
          time=time.split(":")
          time=list(map(int,time))
        if(len(time)==0):
          time.append(0)
        delete_bool=delete_appointment(poi,name,day,time)
        if delete_bool==1:
          conversation.append("Chatbot: Sorry, I was not able to find the required person in the database")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

        elif delete_bool==2:
          conversation.append("Chatbot: Sorry, the person you mentioned does not have a meeting with you at that time")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

        else:
          conversation.append("Chatbot: Appointment has been successfully deleted")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          cust_details["Customer Name"] = name
          meeting = {}
          meeting["poi"] = poi
          tdate = date.copy()
          tdate[0] += day
          tstr = [str(i) for i in tdate]
          meeting["date"] = "-".join(tstr)
          meeting["time"] = time_str
          meeting["location"] = prof[poi.lower()][3]
          meeting_data.append(meeting)
          conversation.append("Chatbot: To further contact you about the meeting, kindly provide e-mail adress and phone number")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          
          email = input("You: Email - ").strip()
          conversation.append("You: Email - "+email)
          phone = input("You: Phone Number - ").strip()
          conversation.append("You: Phone Number - "+phone)
          cust_details["Phone Number"]=phone
          cust_details["Email"]=email
          generate_report(cust_details,meeting_data,conversation,"Cancelled a meeting")
      else:
        poi=""
        name=""
        day=""
        time=""
        for i in key_words:
          if i[0].lower() in prof:
            poi=i[0]
            key_words.remove(i)
            break
        for i in key_words:
          if i[1]=="PERSON":
            name=i[0]
          if i[1]=="DATE":
            day=i[0]
          if i[1]=="TIME":
            time=i[0]
        if poi=="":
          conversation.append("Chatbot: Kindly provide name of person with which your meeting is")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                poi = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {poi}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                poi = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {poi}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+poi)
        if name=="":
          conversation.append("Chatbot: Kindly provide your name for verification")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                name = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {name}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                name = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {name}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+name)
        if day=="":
          conversation.append("Chatbot: Kindly provide day of meeting")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                day = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {day}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                day = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {day}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          conversation.append("You: "+day)
        if time=="":
          conversation.append("Chatbot: Kindly provide time of meeting")
          translated_ = translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

          if mode == 'speak':
              extra_prompt = "Please say the time clearly"
              translated_ = translate(extra_prompt, source_lang_num=1, target_lang_num=lang_num, gender=gender)
              tts(translated_, lang_num)
              play_audio("output.wav")
              t.sleep(1)

              while True:
                  record_audio("user_input.wav", duration=5)
                  time = stt_translate("user_input.wav").strip()
                  print(f"You (spoken → translated to English): {time}")
                  c = input("Is the recording satisfactory? Y/N: ").strip()
                  if c.lower() == 'y':
                      break
          else:
              time = input("You: ").strip()

          conversation.append("You: "+time)
        day=add_day(day)
        time_str=time
        time=time.split()
        if len(time)>1:
          time[0]=time[0].split(":")
          time[0]=list(map(int,time[0]))
          if time[1].lower()=="pm" and time[0][0]!=12:
            time[0][0]+=12
          time=time[0]
        else:
          time=time[0]
          time=time.split(":")
          time=list(map(int,time))
        if(len(time)==0):
          time.append(0)
        check_bool=check_appointment(poi,name,day,time)
        if check_bool==1:
          conversation.append("Chatbot: Sorry, I was not able to find the required person in the database")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
        elif check_bool==2:
          conversation.append("Chatbot: Sorry, I was unable to find your meeting with the required person in the database")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
        else:
          cust_details["Customer Name"] = name
          meeting = {}
          meeting["poi"] = poi
          tdate = date.copy()
          tdate[0] += day
          tstr = [str(i) for i in tdate]
          meeting["date"] = "-".join(tstr)
          meeting["time"] = time_str
          meeting["location"] = prof[poi.lower()][3]
          meeting_data.append(meeting)
          conversation.append(f'Chatbot: Welcome{" "+name}. Your meeting with {gender_find(prof[poi.lower()][0])} {prof[poi.lower()][1]} is confirmed. Please proceed to the {prof[poi.lower()][2]} to room no. {prof[poi.lower()][3]} at the required time')
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          conversation.append(f'Chatbot: Should I provide instructions to the {prof[poi.lower()][2]}?')
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          conversation.append("You: "+choice)
          choice=""
          mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()
          if mode == 'speak':
              while True:
                record_audio("user_input.wav", duration=5)
                choice = stt_translate("user_input.wav").strip()
                print(f"You (spoken → translated to English): {choice}")
                c = input("Is the recording satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                  break 
          else:
              while True:
                typed_input = input("You (in native language): ").strip()
                choice = translate(typed_input, lang_num, 1, gender).strip()
                print(f"You (typed → translated to English): {choice}")
                c = input("Is the translation satisfactory? Y/N: ").strip()
                if c.lower() == 'y':
                    break
          if choice in ["No","NO","no","n"]:
            pass
          else:
            conversation.append(f'Chatbot: Understood. Here are the instructions to the {prof[poi.lower()][2]}.')
            translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
            print(translated_)
            tts(translated_, lang_num)
            play_audio("output.wav")
            t.sleep(1)
            conversation.append("Chatbot: "+directions[prof[poi.lower()][2]])
            translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
            print(translated_)
            tts(translated_, lang_num)
            play_audio("output.wav")
            t.sleep(1)
          conversation.append("Chatbot: To further contact you about the meeting, kindly provide e-mail adress and phone number")
          translated_= translate(conversation[-1].split(":")[1], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          email = input("You: Email - ").strip()
          conversation.append("You: Email - "+email)
          phone = input("You: Phone Number - ").strip()
          conversation.append("You: Phone Number - "+phone)
          cust_details["Phone Number"]=phone
          cust_details["Email"]=email
          generate_report(cust_details,meeting_data,conversation,"Viewed a meeting")
    else:
      poi=""
      name=""
      for i in key_words:
        if i[0].lower() in prof:
          poi=i[0]
          key_words.remove(i)
          break
      for i in key_words:
        if i[1]=="PERSON":
          name=i[0]
      if poi!="":
        translated_= translate(f'Chatbot: Welcome{" "+name}. I have notified {gender_find(prof[poi.lower()][0])} {prof[poi.lower()][1]} of your arrival. Please proceed to the {prof[poi.lower()][2]} to room no. {prof[poi.lower()][3]}', source_lang_num=1, target_lang_num=lang_num, gender=gender)
        print(translated_)
        tts(translated_, lang_num)
        play_audio("output.wav")
        t.sleep(1)
        translated_= translate(f'Chatbot: Should I provide instructions to the {prof[poi.lower()][2]}?', source_lang_num=1, target_lang_num=lang_num, gender=gender)
        print(translated_)
        tts(translated_, lang_num)
        play_audio("output.wav")
        t.sleep(1)

        mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()

        if mode == 'speak':
            while True:
              record_audio("user_input.wav", duration=5)
              choice = stt_translate("user_input.wav").strip()
              print(f"You (spoken → translated to English): {poi}")
              c = input("Is the recording satisfactory? Y/N: ").strip()
              if c.lower() == 'y':
                break 
        else:
            while True:
              typed_input = input("You (in native language): ").strip()
              choice = translate(typed_input, lang_num, 1, gender).strip()
              print(f"You (typed → translated to English): {poi}")
              c = input("Is the translation satisfactory? Y/N: ").strip()
              if c.lower() == 'y':
                  break
        
        if choice in ["No","NO","no","n","N"]:
          print("Chatbot: Thank You")
        else:
          translated_= translate(f'Chatbot: Understood. Here are the instructions to the {prof[poi.lower()][2]}.', source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
          
          translated_= translate("Chatbot: Understood"+directions[prof[poi.lower()][2]], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
      else:
        if loc!="":
          print()
          translated_= translate(f'Chatbot: Welcome{name}. Providing directions to the required location: {loc[1]}.', source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)

          print("Chatbot: ",end="")
          translated_= translate("Chatbot: "+directions[loc[1]], source_lang_num=1, target_lang_num=lang_num, gender=gender)
          print(translated_)
          tts(translated_, lang_num)
          play_audio("output.wav")
          t.sleep(1)
        else:
            translated_= translate('Sorry I was unable to understand your query. Please try again.',source_lang_num=1, target_lang_num=lang_num, gender=gender)
            print(translated_)
            tts(translated_, lang_num)
            play_audio("output.wav")
            t.sleep(1)
    
    cust_data = {}
    cust_data["Personal"] = cust_details
    cust_data["Meetings"] = meeting_data

    if cust_data["Meetings"] != []:
        # Encrypt Phone Number & Email
        cust_data["Personal"]["Phone Number"] = encrypt_data(cust_data["Personal"]["Phone Number"])
        cust_data["Personal"]["Email"] = encrypt_data(cust_data["Personal"]["Email"])

        # Update MongoDB entry
        collection.update_one(
            {"Personal.Customer Name": cust_data["Personal"]["Customer Name"]},  # Find by name
            {
                "$set": {
                    "Personal.Phone Number": cust_data["Personal"]["Phone Number"],
                    "Personal.Email": cust_data["Personal"]["Email"]
                },
                "$push": {"Meetings": meeting_data}  # Append all new meetings
            },
            upsert=True  # Insert if not found
      )
    goodbye_text = "Thank you for visiting .Can I do anything else to be of service today?"
    translated_= translate(goodbye_text, source_lang_num=1, target_lang_num=lang_num, gender=gender)
    tts(translated_,2)
    play_audio("output.wav")
    t.sleep(1)
    choice_final=""
    mode = input("Type 'speak' to talk or press enter to type: ").strip().lower()
    if mode == 'speak':
        while True:
          record_audio("user_input.wav", duration=5)
          choice_final = stt_translate("user_input.wav").strip()
          print(f"You (spoken → translated to English): {choice_final}")
          c = input("Is the recording satisfactory? Y/N: ").strip()
          if c.lower() == 'y':
            break 
    else:
        while True:
          typed_input = input("You (in native language): ").strip()
          choice_final = translate(typed_input, lang_num, 1, gender).strip()
          print(f"You (typed → translated to English): {choice_final}")
          c = input("Is the translation satisfactory? Y/N: ").strip()
          if c.lower() == 'y':
              break
    if choice_final.strip().lower() in "non":
       break

def get_customer_data(authenticated_role, customer_name):
    customer = collection.find_one({"Personal.Customer Name": customer_name})

    if not customer:
        return "Customer not found."

    if authenticated_role == "admin":
        customer["Personal"]["Phone Number"] = decrypt_data(customer["Personal"]["Phone Number"])
        customer["Personal"]["Email"] = decrypt_data(customer["Personal"]["Email"])
    else:
        customer["Personal"]["Phone Number"] = "[ENCRYPTED]"
        customer["Personal"]["Email"] = "[ENCRYPTED]"

    return customer
def authenticate_user(username, password):
    users_db = client["Users"]
    admins_db = client["Admins"]

    user = users_db["User_1"].find_one({"Name": username, "Password": password})
    admin = admins_db["Admin_1"].find_one({"Name": username, "Password": password})

    if admin:
        return "admin"
    elif user:
        return "user"
    else:
        return None

def menu():

    while True:
        print("\nMain Menu:")
        print("1. Chatbot (Multilingual)")
        print("2. Data Access")
        print("3. Exit")
        c = input("Choose an option (1/2/3): ").strip()

        if c == "1":
            print("Select a language:")
            print("1 - English\n2 - Hindi\n3 - Bengali\n4 - Gujarati\n5 - Kannada\n6 - Malayalam\n7 - Marathi\n8 - Odia\n9 - Punjabi\n10 - Tamil\n11 - Telugu")
            try:
                lang_num = int(input("Enter number corresponding to language: ").strip())
                if lang_num not in range(1, 12):
                    print("Invalid language selection. Returning to main menu.")
                    continue
            except ValueError:
                print("Please enter a valid number. Returning to main menu.")
                continue

            gender=input("Enter speaker gender (Male/Female): ").strip()
            print("Redirecting you to our chatbot... thank you for visiting us!")
            chatbot(lang_num, gender)

        elif c == "2":
            username=input("Enter Username: ").strip()
            password=input("Enter Password: ").strip()
            role = authenticate_user(username, password)
            if role:
                print(f"Authenticated as {role}.")
                while True:
                    customer_name=input("Enter Customer Name: ").strip()
                    customer_data=get_customer_data(role, customer_name)
                    print(customer_data)
                    c = input("Do you want to view another? (Y/N): ").strip()
                    if c.lower()=="n":
                        break
            else:
                print("Authentication failed.")
        elif c=="3":
            print("Thanks for visiting.")
            break
        else:
            print("Invalid choice. Please choose 1, 2, or 3.")
menu()
