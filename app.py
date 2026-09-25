from flask import Flask, request, jsonify, render_template
import os
import datetime
import requests
import json
import wikipedia
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from email.message import EmailMessage
import smtplib

app = Flask(__name__)

# Configure NLTK for Vercel's read-only filesystem
nltk.data.path.append('/tmp/nltk_data')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir='/tmp/nltk_data')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir='/tmp/nltk_data')

def parse_intent(command):
    command = command.lower()
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

    if "hello" in command or "hi" in command:
        return "greet", None
    elif "time" in command:
        return "time", None
    elif "date" in command:
        return "date", None
    elif "search" in command:
        parts = command.split("search", 1)
        query = parts[1].strip() if len(parts) > 1 else ""
        if query.startswith("for "):
            query = query[4:]
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
    response_text = ""
    action = None

    if intent == "greet":
        response_text = "Hello! How can I help you today?"
    
    elif intent == "time":
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        response_text = f"The current time is {current_time}"
    
    elif intent == "date":
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        response_text = f"Today's date is {current_date}"
    
    elif intent == "search":
        if payload:
            response_text = f"Searching the web for {payload}"
            action = {"type": "search", "query": payload}
        else:
            response_text = "What would you like me to search for?"
            
    elif intent == "weather":
        api_key = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
        if api_key == "YOUR_API_KEY_HERE" or not api_key:
            response_text = "Please configure your OpenWeatherMap API key in the backend environment variables."
        else:
            city = "London" 
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            try:
                res = requests.get(url).json()
                if res.get("cod") == 200:
                    weather_desc = res["weather"][0]["description"]
                    temp = res["main"]["temp"]
                    response_text = f"The weather in {city} is {weather_desc} with a temperature of {temp} degrees Celsius."
                else:
                    response_text = "I couldn't fetch the weather for that location."
            except Exception as e:
                response_text = "Could not fetch the weather details right now."
            
    elif intent == "email":
        sender = os.environ.get("EMAIL_USER")
        password = os.environ.get("EMAIL_PASS")
        recipient = os.environ.get("TEST_EMAIL_RECIPIENT", sender)
        
        if not sender or not password:
            response_text = "Email credentials are not configured on the server. Please check environment setup."
        else:
            response_text = "Sending a test email."
            try:
                msg = EmailMessage()
                msg.set_content("This is an automated message sent by the Python Voice Assistant via Web UI.")
                msg['Subject'] = 'Hello from Voice Assistant Web'
                msg['From'] = sender
                msg['To'] = recipient

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
                server.quit()
                response_text += " Email sent successfully."
            except Exception as e:
                response_text = "Failed to send email. Check credentials."
            
    elif intent == "reminder":
        response_text = "I have set a reminder for 10 seconds from now."
        action = {"type": "reminder", "duration": 10}
        
    elif intent == "qa":
        query = payload.replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
        if query:
            try:
                result = wikipedia.summary(query, sentences=2)
                response_text = result
            except wikipedia.exceptions.DisambiguationError:
                response_text = "The topic is too broad. Please be more specific."
            except wikipedia.exceptions.PageError:
                response_text = "I couldn't find any information on that topic."
            except Exception:
                response_text = "An error occurred while fetching information."
        else:
            response_text = "What would you like to know?"
            
    elif intent == "add_command":
        response_text = "Custom command configuration is restricted on the web version."
                
    elif intent == "custom":
        response_text = payload
        
    else:
        response_text = "I am not sure how to help with that. Try asking for the time, weather, or to search the web."

    return response_text, action

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    command = data.get("command", "")
    if not command:
        return jsonify({"text": "No command provided", "action": None})
    
    intent, payload = parse_intent(command)
    response_text, action = execute_intent(intent, payload)
    
    return jsonify({"text": response_text, "action": action})

if __name__ == '__main__':
    app.run(debug=True)
