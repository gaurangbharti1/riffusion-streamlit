import streamlit as st
import requests
import time

API_KEY = str(st.secrets["SIEVE_API_KEY"])

st.title("Stable Riffusion")
st.markdown('Built by [Gaurang Bharti](https://twitter.com/gaurang_bharti) powered by [Sieve](https://www.sievedata.com)')
st.markdown("This web app uses [Stable Riffusion](https://github.com/riffusion/riffusion) to generate music using an input text prompt")

def check_status(url, interval, job_id):
    finished = False
    headers = {
        'X-API-Key': API_KEY
        }
    while True:
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        for job in data:
            if job['id'] == job_id:
            
                if job['status'] == 'processing':
              
                    time.sleep(interval)
                if job['status'] == 'finished':
                   
                    finished = True
                    return finished
                if job['status'] == 'error':
                    st.error("An error occured, please try again. If the error persists, please inform the developers.")
                    print(job['error'])
                    return job['error']

def fetch_video(job_id):
    url = f"https://mango.sievedata.com/v1/jobs/{job_id}"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    response = requests.get(url, headers = headers)
    data = response.json()
    url = data['data'][0]['url']
    return url

def send_data(text, duration, name):
    url = "https://mango.sievedata.com/v1/push"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    } 
    data = {
        "workflow_name": name,
        "inputs": {
            "prompt": text,
            "duration": duration
            }
        }
    try:
        response = requests.post(url, headers=headers, json=data)
        if ('id') not in response.json():
            st.error(response.json()['description'])
            return False
        return (response.json()['id'])
    except Exception as e:
        return (f'An error occurred: {e}')
    
#Streamlit App

text_in = st.text_input('Enter prompt', max_chars=100)
st.write('Examples: acoustic folk violin jam,  scott joplin style ragtime piano, swing jazz trumpet')
input_duration = st.slider("Duration (seconds)", 4, 8, 5)
workflow_name = "stable-riffusion"

button1 = st.button("Riffusion")

if st.session_state.get('button') != True:
    st.session_state['button'] = button1

if st.session_state['button'] == True:

    job = send_data(text_in, input_duration, workflow_name)
    if job:
        with st.spinner("Processing Audio"):
            status = check_status('https://mango.sievedata.com/v1/jobs', 5, str(job))
            if status == True:
                audio = fetch_video(job)
                st.audio(audio)