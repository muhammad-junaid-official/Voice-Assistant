import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import smtplib
import requests
import json
import threading
import time
import os
import wikipedia
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from email.message import EmailMessage

# Ensure necessary NLTK data is downloaded
# Using a local directory for NLTK data to keep the project contained or download on first run
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # Adjust for ambient noise and listen
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
            command = recognizer.recognize_google(audio)
            print(f"User: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            speak("There seems to be an issue with the speech recognition service.")
            print(f"Error: {e}")
            return None
        except Exception as e:
            return None

def parse_intent(command):
    """
    Basic Natural Language Understanding:
    Tokenizes input and removes stop words to help find key intents.
    """
    tokens = word_tokenize(command)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in tokens if w not in stop_words]
    
    # Check custom commands first
    if os.path.exists("custom_commands.json"):
        try:
            with open("custom_commands.json", "r") as f:
                custom_commands = json.load(f)
                for cmd, action in custom_commands.items():
                    if cmd in command:
                        return "custom", action
        except:
            pass

    # Intent matching
    if "hello" in command or "hi" in command:
        return "greet", None
    elif "time" in command:
        return "time", None
    elif "date" in command:
        return "date", None
    elif "search" in command:
        query = command.split("search", 1)[1].strip()
        return "search", query
    elif "weather" in command:
        return "weather", command
    elif "email" in command:
        return "email", None
    elif "remind me" in command or "reminder" in command:
        return "reminder", command
    elif "what is" in command or "who is" in command or "tell me about" in command:
        return "qa", command
    elif "add command" in command:
        return "add_command", None
    else:
        return "unknown", command

def execute_intent(intent, payload):
    if intent == "greet":
        speak("Hello! How can I help you today?")
    
    elif intent == "time":
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
    
    elif intent == "date":
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    
    elif intent == "search":
        if payload:
            speak(f"Searching the web for {payload}")
            webbrowser.open(f"https://www.google.com/search?q={payload}")
        else:
            speak("What would you like me to search for?")
            
    elif intent == "weather":
        api_key = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
        if api_key == "YOUR_API_KEY_HERE" or not api_key:
            speak("Please configure your OpenWeatherMap API key in the environment variables.")
            return
            
        # Default city, could be improved by extracting city from the payload
        city = "London" 
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            res = requests.get(url).json()
            if res.get("cod") == 200:
                weather_desc = res["weather"][0]["description"]
                temp = res["main"]["temp"]
                speak(f"The weather in {city} is {weather_desc} with a temperature of {temp} degrees Celsius.")
            else:
                speak("I couldn't fetch the weather for that location.")
        except Exception as e:
            speak("Could not fetch the weather details right now.")
            
    elif intent == "email":
        sender = os.environ.get("EMAIL_USER")
        password = os.environ.get("EMAIL_PASS")
        recipient = os.environ.get("TEST_EMAIL_RECIPIENT", sender)
        
        if not sender or not password:
            speak("Email credentials are not configured. Please check your environment setup.")
            return
            
        speak("Sending a test email.")
        try:
            msg = EmailMessage()
            msg.set_content("This is an automated message sent by the Python Voice Assistant.")
            msg['Subject'] = 'Hello from Voice Assistant'
            msg['From'] = sender
            msg['To'] = recipient

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            speak("Email sent successfully.")
        except Exception as e:
            speak("Failed to send email.")
            print(f"Error: {e}")
            
    elif intent == "reminder":
        speak("I have set a reminder for 10 seconds from now.")
        def reminder_thread():
            time.sleep(10)
            speak("Reminder: Time is up! This is your alert.")
        threading.Thread(target=reminder_thread, daemon=True).start()
        
    elif intent == "qa":
        # Clean up the query for Wikipedia
        query = payload.replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
        if query:
            speak(f"Looking up {query} on Wikipedia...")
            try:
                # Get a brief summary
                result = wikipedia.summary(query, sentences=2)
                speak(result)
            except wikipedia.exceptions.DisambiguationError as e:
                speak("The topic is too broad. Please be more specific.")
            except wikipedia.exceptions.PageError:
                speak("I couldn't find any information on that topic.")
            except Exception:
                speak("An error occurred while fetching information.")
        else:
            speak("What would you like to know?")
            
    elif intent == "add_command":
        speak("To add a custom command, please edit the custom_commands.json file directly.")
        if not os.path.exists("custom_commands.json"):
            with open("custom_commands.json", "w") as f:
                json.dump({"test command": "This is a custom response"}, f, indent=4)
                
    elif intent == "custom":
        speak(payload)
        
    else:
        speak("I am not sure how to help with that. Try asking for the time, weather, or to search the web.")

def main():
    speak("Voice assistant is initializing...")
    while True:
        command = listen()
        if command:
            if any(word in command for word in ["stop", "exit", "quit", "goodbye"]):
                speak("Goodbye!")
                break
            intent, payload = parse_intent(command)
            execute_intent(intent, payload)

if __name__ == "__main__":
    main()
