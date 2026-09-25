# Python Voice Assistant

A feature-rich Python voice assistant that listens to spoken commands and responds with useful actions, implementing both beginner and advanced features.

## Features

### Beginner Tier
- **Voice Input**: Captures voice using the `speech_recognition` library (Microphone).
- **Greetings**: Responds to "Hello" or "Hi".
- **Time and Date**: Tells the current time and date when asked.
- **Web Search**: Opens the browser and searches Google for user-specified topics.
- **Error Handling**: Gracefully handles unrecognized voice inputs and prompts the user to repeat.
- **Text-to-Speech**: Provides audible feedback using `pyttsx3`.

### Advanced Tier
- **Natural Language Understanding (NLU)**: Parses intents from free-form sentences using `nltk` (tokenization & stop words removal).
- **Email Sending**: Sends an email via voice command using `smtplib` (requires configuration).
- **Reminders**: Sets timed reminders that trigger an audible alert in a background thread.
- **Live Weather**: Fetches and reads live weather updates using the OpenWeatherMap API.
- **QA Capabilities**: Answers general knowledge questions using the Wikipedia API.
- **Custom Commands**: Easily extensible by adding custom voice triggers and responses in `custom_commands.json`.

## Requirements

- Python 3.7+
- PyAudio (required for microphone input)

Install dependencies using:
```bash
pip install -r requirements.txt
```

*Note: On Windows, installing PyAudio might require downloading a precompiled wheel if the build fails.*

## Configuration

For advanced features like Weather and Email, create a `.env` file in the root directory and add your credentials (or export them as environment variables):

```env
OPENWEATHER_API_KEY=your_openweathermap_api_key
EMAIL_USER=your_dummy_gmail@gmail.com
EMAIL_PASS=your_app_password
TEST_EMAIL_RECIPIENT=recipient@gmail.com
```

## Privacy Notice (Data Processing)

**Data Processing & Privacy**:
- **Microphone Data**: The voice data captured via the microphone is sent to Google's Speech Recognition API (by default) to convert speech to text. This data is transmitted over the internet to Google's servers.
- **Weather API**: If you request weather data, the city name (or default location) is sent to the OpenWeatherMap API to retrieve weather information.
- **Search & Knowledge Base**: Search queries and general knowledge questions are sent to Google Search (via browser URL) and the Wikipedia API, respectively.
- **Local Processing**: NLTK tokenization, time/date logic, and text-to-speech are processed locally on your machine.
- **Credentials**: Any API keys or email credentials are kept locally. Make sure not to commit them to public repositories (they should be stored in a `.env` file excluded by `.gitignore`).

## Usage

Run the assistant script from your terminal:

```bash
python assistant.py
```

Try commands like:
- "Hello"
- "What is the time?"
- "What is the date today?"
- "Search for Python programming"
- "What is the weather?"
- "Tell me about artificial intelligence"
- "Remind me"
- "Send an email"
- "Exit"
