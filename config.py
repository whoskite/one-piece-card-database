"""
Configuration settings for the One Piece Card Database.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base URL for the One Piece Card Game website
BASE_URL = "https://asia-en.onepiece-cardgame.com/cardlist/"

# User agent for web requests
USER_AGENT = os.getenv(
    "USER_AGENT", 
    "One Piece Card Database Project (https://github.com/whoskite/one-piece-card-database)"
)

# Delay between requests (in seconds)
REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "2"))

# Output directory for scraped data
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data")

# Database settings
DB_PATH = os.getenv("DB_PATH", os.path.join(OUTPUT_DIR, "one_piece_cards.db"))

# Selenium settings
HEADLESS = os.getenv("HEADLESS", "True").lower() in ("true", "1", "t")
BROWSER_WIDTH = int(os.getenv("BROWSER_WIDTH", "1920"))
BROWSER_HEIGHT = int(os.getenv("BROWSER_HEIGHT", "1080"))

# Card colors
CARD_COLORS = [
    "Red",
    "Green",
    "Blue",
    "Purple",
    "Black",
    "Yellow",
    "Multicolor"
]

# Card types
CARD_TYPES = [
    "Leader",
    "Character",
    "Event",
    "Stage"
]