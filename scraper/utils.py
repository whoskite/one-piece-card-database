"""
Utility functions for the One Piece card scraper.
"""
import os
import re
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://asia-en.onepiece-cardgame.com/cardlist/"
USER_AGENT = "One Piece Card Database Project (https://github.com/whoskite/one-piece-card-database)"
REQUEST_DELAY = 2  # seconds between requests


def get_page(url: str, params: Optional[Dict[str, Any]] = None) -> BeautifulSoup:
    """
    Fetch a page and return a BeautifulSoup object.
    
    Args:
        url: The URL to fetch
        params: Optional query parameters
        
    Returns:
        BeautifulSoup object of the page
    """
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        logger.info(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # Add delay to be respectful to the server
        time.sleep(REQUEST_DELAY)
        
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        raise


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and newlines.
    
    Args:
        text: The text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def extract_card_id_parts(card_id: str) -> Tuple[str, str, str]:
    """
    Extract set code, card number, and rarity from a card ID.
    
    Args:
        card_id: The card ID (e.g., "OP01-001 SR")
        
    Returns:
        Tuple of (set_code, card_number, rarity)
    """
    # Pattern: SET-NUMBER RARITY
    pattern = r'([A-Z0-9]+)-(\d+)\s*([A-Z]+)?'
    match = re.match(pattern, card_id)
    
    if match:
        set_code = match.group(1)
        card_number = match.group(2)
        rarity = match.group(3) if match.group(3) else ""
        return set_code, card_number, rarity
    
    return "", "", ""


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")


def parse_cost(cost_text: str) -> Optional[int]:
    """
    Parse the cost value from text.
    
    Args:
        cost_text: The cost text
        
    Returns:
        Integer cost or None if not a valid cost
    """
    if not cost_text or cost_text.strip() == "-":
        return None
    
    try:
        return int(cost_text.strip())
    except ValueError:
        return None