import os
from dotenv import load_dotenv

load_dotenv()

# Plivo Credentials
PLIVO_AUTH_ID = os.getenv("PLIVO_AUTH_ID")
PLIVO_AUTH_TOKEN = os.getenv("PLIVO_AUTH_TOKEN")

# Phone Numbers
PLIVO_FROM_NUMBER = os.getenv("PLIVO_FROM_NUMBER")
ASSOCIATE_NUMBER = os.getenv("ASSOCIATE_NUMBER")

# Base URL for webhooks (ngrok URL in development)
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# Audio URLs (publicly accessible MP3 files)
AUDIO_URL_EN = "https://s3.amazonaws.com/plivocloud/Trumpet.mp3"
AUDIO_URL_ES = "https://s3.amazonaws.com/plivocloud/Trumpet.mp3"
