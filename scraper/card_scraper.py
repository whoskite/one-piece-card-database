"""
Main scraper for One Piece Card Game cards.
"""
import json
import logging
import os
import re
import time
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from scraper.models import Card
from scraper.utils import (
    BASE_URL, 
    get_page, 
    clean_text, 
    extract_card_id_parts, 
    ensure_directory,
    parse_cost
)

# Configure logging
logger = logging.getLogger(__name__)

class OnePieceCardScraper:
    """Scraper for One Piece Card Game cards."""
    
    def __init__(self, headless: bool = True, output_dir: str = "data"):
        """
        Initialize the scraper.
        
        Args:
            headless: Whether to run the browser in headless mode
            output_dir: Directory to save scraped data
        """
        self.output_dir = output_dir
        ensure_directory(output_dir)
        
        # Set up Selenium
        self.headless = headless
        self.driver = None
        
        # Card data storage
        self.cards = []
        
    def setup_driver(self) -> None:
        """Set up the Selenium WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument(f"user-agent=One Piece Card Database Project (https://github.com/whoskite/one-piece-card-database)")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def close_driver(self) -> None:
        """Close the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def scrape_all_cards(self, max_pages: Optional[int] = None) -> List[Card]:
        """
        Scrape all cards from the website.
        
        Args:
            max_pages: Maximum number of pages to scrape (for testing)
            
        Returns:
            List of Card objects
        """
        try:
            self.setup_driver()
            self.driver.get(BASE_URL)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cardlist-item"))
            )
            
            page = 1
            has_more = True
            
            while has_more and (max_pages is None or page <= max_pages):
                logger.info(f"Scraping page {page}")
                
                # Extract cards from current page
                page_html = self.driver.page_source
                soup = BeautifulSoup(page_html, 'html.parser')
                
                # Find all card items on the page
                card_items = soup.select(".cardlist-item")
                
                if not card_items:
                    logger.warning("No card items found on page")
                    break
                
                for card_item in card_items:
                    card = self._parse_card_item(card_item)
                    if card:
                        self.cards.append(card)
                
                # Check if there's a "NEXT" button
                try:
                    next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'NEXT')]")
                    if next_button.is_enabled():
                        next_button.click()
                        # Wait for the new cards to load
                        time.sleep(3)
                        page += 1
                    else:
                        has_more = False
                except NoSuchElementException:
                    # Try the "Add more" button
                    try:
                        add_more = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add more')]")
                        add_more.click()
                        # Wait for the new cards to load
                        time.sleep(3)
                        page += 1
                    except NoSuchElementException:
                        has_more = False
            
            logger.info(f"Scraped {len(self.cards)} cards from {page} pages")
            return self.cards
            
        except Exception as e:
            logger.error(f"Error scraping cards: {e}")
            raise
        finally:
            self.close_driver()
    
    def scrape_with_filters(self, color: Optional[str] = None, card_type: Optional[str] = None) -> List[Card]:
        """
        Scrape cards with specific filters.
        
        Args:
            color: Filter by card color
            card_type: Filter by card type
            
        Returns:
            List of Card objects
        """
        try:
            self.setup_driver()
            
            # Build the URL with filters
            url = BASE_URL
            params = {}
            
            if color:
                params['color'] = color
            if card_type:
                params['cardtype'] = card_type
                
            # Add parameters to URL
            if params:
                query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                url = f"{url}?{query_string}"
            
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cardlist-item"))
            )
            
            # Now scrape the filtered results
            return self.scrape_all_cards()
            
        except Exception as e:
            logger.error(f"Error scraping with filters: {e}")
            raise
        finally:
            self.close_driver()
    
    def _parse_card_item(self, card_item: Tag) -> Optional[Card]:
        """
        Parse a card item from the page.
        
        Args:
            card_item: BeautifulSoup Tag containing card information
            
        Returns:
            Card object or None if parsing failed
        """
        try:
            # Extract card details
            card_id_elem = card_item.select_one(".card-id")
            name_elem = card_item.select_one(".card-name")
            
            if not card_id_elem or not name_elem:
                logger.warning("Missing required card elements")
                return None
            
            card_id = clean_text(card_id_elem.text)
            name = clean_text(name_elem.text)
            
            # Extract card type and rarity from the card ID
            set_code, card_number, rarity = extract_card_id_parts(card_id)
            
            # Extract other card details
            card_type = clean_text(card_item.select_one(".card-type").text) if card_item.select_one(".card-type") else ""
            cost = parse_cost(clean_text(card_item.select_one(".card-cost").text)) if card_item.select_one(".card-cost") else None
            attribute = clean_text(card_item.select_one(".card-attribute").text) if card_item.select_one(".card-attribute") else ""
            power = clean_text(card_item.select_one(".card-power").text) if card_item.select_one(".card-power") else ""
            counter = clean_text(card_item.select_one(".card-counter").text) if card_item.select_one(".card-counter") else ""
            color = clean_text(card_item.select_one(".card-color").text) if card_item.select_one(".card-color") else ""
            character_type = clean_text(card_item.select_one(".card-character-type").text) if card_item.select_one(".card-character-type") else ""
            effect = clean_text(card_item.select_one(".card-effect").text) if card_item.select_one(".card-effect") else ""
            trigger_effect = clean_text(card_item.select_one(".card-trigger").text) if card_item.select_one(".card-trigger") else ""
            card_set = clean_text(card_item.select_one(".card-set").text) if card_item.select_one(".card-set") else ""
            
            # Extract image URL
            image_elem = card_item.select_one("img")
            image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else ""
            
            # Create Card object
            return Card(
                card_id=card_id,
                name=name,
                card_type=card_type,
                rarity=rarity,
                cost=cost,
                attribute=attribute,
                power=power,
                counter=counter,
                color=color,
                character_type=character_type,
                effect=effect,
                trigger_effect=trigger_effect,
                card_set=card_set,
                image_url=image_url
            )
            
        except Exception as e:
            logger.error(f"Error parsing card item: {e}")
            return None
    
    def save_to_csv(self, filename: str = "one_piece_cards.csv") -> str:
        """
        Save the scraped cards to a CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            Path to the saved file
        """
        if not self.cards:
            logger.warning("No cards to save")
            return ""
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert cards to dictionaries
        cards_dict = [card.to_dict() for card in self.cards]
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(cards_dict)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Saved {len(self.cards)} cards to {filepath}")
        return filepath
    
    def save_to_json(self, filename: str = "one_piece_cards.json") -> str:
        """
        Save the scraped cards to a JSON file.
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            Path to the saved file
        """
        if not self.cards:
            logger.warning("No cards to save")
            return ""
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert cards to dictionaries
        cards_dict = [card.to_dict() for card in self.cards]
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cards_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.cards)} cards to {filepath}")
        return filepath