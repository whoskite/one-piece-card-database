"""
Database manager for One Piece card database.
"""
import os
import sqlite3
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from scraper.models import Card
from scraper.utils import ensure_directory

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manager for the One Piece card database."""
    
    def __init__(self, db_path: str = "data/one_piece_cards.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        ensure_directory(os.path.dirname(db_path))
        self.conn = None
        self.cursor = None
    
    def connect(self) -> None:
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Database connection closed")
    
    def initialize_database(self) -> None:
        """Initialize the database with the schema."""
        try:
            self.connect()
            
            # Read the schema SQL file
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute the schema SQL
            self.conn.executescript(schema_sql)
            self.conn.commit()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            self.close()
    
    def insert_cards(self, cards: List[Card]) -> int:
        """
        Insert cards into the database.
        
        Args:
            cards: List of Card objects to insert
            
        Returns:
            Number of cards inserted
        """
        try:
            self.connect()
            
            inserted_count = 0
            
            for card in cards:
                try:
                    # Check if card already exists
                    self.cursor.execute("SELECT id FROM cards WHERE card_id = ?", (card.card_id,))
                    existing_card = self.cursor.fetchone()
                    
                    if existing_card:
                        # Update existing card
                        self.cursor.execute("""
                            UPDATE cards SET
                                name = ?,
                                card_type = ?,
                                rarity = ?,
                                cost = ?,
                                attribute = ?,
                                power = ?,
                                counter = ?,
                                color = ?,
                                character_type = ?,
                                effect = ?,
                                trigger_effect = ?,
                                card_set = ?,
                                image_url = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE card_id = ?
                        """, (
                            card.name,
                            card.card_type,
                            card.rarity,
                            card.cost,
                            card.attribute,
                            card.power,
                            card.counter,
                            card.color,
                            card.character_type,
                            card.effect,
                            card.trigger_effect,
                            card.card_set,
                            card.image_url,
                            card.card_id
                        ))
                    else:
                        # Insert new card
                        self.cursor.execute("""
                            INSERT INTO cards (
                                card_id, name, card_type, rarity, cost, attribute,
                                power, counter, color, character_type, effect,
                                trigger_effect, card_set, image_url
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            card.card_id,
                            card.name,
                            card.card_type,
                            card.rarity,
                            card.cost,
                            card.attribute,
                            card.power,
                            card.counter,
                            card.color,
                            card.character_type,
                            card.effect,
                            card.trigger_effect,
                            card.card_set,
                            card.image_url
                        ))
                        inserted_count += 1
                    
                    # Insert or update card set if available
                    if card.card_set:
                        # Extract set code from card ID
                        set_code = card.card_id.split('-')[0] if '-' in card.card_id else ""
                        
                        if set_code:
                            self.cursor.execute("""
                                INSERT OR IGNORE INTO card_sets (code, name)
                                VALUES (?, ?)
                            """, (set_code, card.card_set))
                    
                    # Insert character types if available
                    if card.character_type:
                        # Character types might be separated by '/'
                        char_types = [t.strip() for t in card.character_type.split('/')]
                        
                        for char_type in char_types:
                            if char_type:
                                self.cursor.execute("""
                                    INSERT OR IGNORE INTO character_types (name)
                                    VALUES (?)
                                """, (char_type,))
                
                except sqlite3.Error as e:
                    logger.error(f"Error inserting card {card.card_id}: {e}")
            
            self.conn.commit()
            logger.info(f"Inserted {inserted_count} new cards into the database")
            
            return inserted_count
        
        except Exception as e:
            logger.error(f"Error inserting cards: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            self.close()
    
    def get_all_cards(self) -> List[Dict[str, Any]]:
        """
        Get all cards from the database.
        
        Returns:
            List of card dictionaries
        """
        try:
            self.connect()
            
            self.cursor.execute("SELECT * FROM cards ORDER BY card_id")
            cards = [dict(row) for row in self.cursor.fetchall()]
            
            logger.info(f"Retrieved {len(cards)} cards from the database")
            return cards
        
        except Exception as e:
            logger.error(f"Error getting all cards: {e}")
            raise
        finally:
            self.close()
    
    def get_cards_by_color(self, color: str) -> List[Dict[str, Any]]:
        """
        Get cards by color.
        
        Args:
            color: Card color to filter by
            
        Returns:
            List of card dictionaries
        """
        try:
            self.connect()
            
            self.cursor.execute("SELECT * FROM cards WHERE color = ? ORDER BY card_id", (color,))
            cards = [dict(row) for row in self.cursor.fetchall()]
            
            logger.info(f"Retrieved {len(cards)} {color} cards from the database")
            return cards
        
        except Exception as e:
            logger.error(f"Error getting cards by color: {e}")
            raise
        finally:
            self.close()
    
    def get_cards_by_type(self, card_type: str) -> List[Dict[str, Any]]:
        """
        Get cards by type.
        
        Args:
            card_type: Card type to filter by
            
        Returns:
            List of card dictionaries
        """
        try:
            self.connect()
            
            self.cursor.execute("SELECT * FROM cards WHERE card_type = ? ORDER BY card_id", (card_type,))
            cards = [dict(row) for row in self.cursor.fetchall()]
            
            logger.info(f"Retrieved {len(cards)} {card_type} cards from the database")
            return cards
        
        except Exception as e:
            logger.error(f"Error getting cards by type: {e}")
            raise
        finally:
            self.close()
    
    def get_cards_by_set(self, set_code: str) -> List[Dict[str, Any]]:
        """
        Get cards by set.
        
        Args:
            set_code: Set code to filter by
            
        Returns:
            List of card dictionaries
        """
        try:
            self.connect()
            
            self.cursor.execute("SELECT * FROM cards WHERE card_id LIKE ? ORDER BY card_id", (f"{set_code}-%",))
            cards = [dict(row) for row in self.cursor.fetchall()]
            
            logger.info(f"Retrieved {len(cards)} cards from set {set_code}")
            return cards
        
        except Exception as e:
            logger.error(f"Error getting cards by set: {e}")
            raise
        finally:
            self.close()
    
    def export_to_csv(self, filepath: str) -> None:
        """
        Export the database to a CSV file.
        
        Args:
            filepath: Path to the CSV file
        """
        try:
            cards = self.get_all_cards()
            
            if not cards:
                logger.warning("No cards to export")
                return
            
            df = pd.DataFrame(cards)
            df.to_csv(filepath, index=False)
            
            logger.info(f"Exported {len(cards)} cards to {filepath}")
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def export_to_json(self, filepath: str) -> None:
        """
        Export the database to a JSON file.
        
        Args:
            filepath: Path to the JSON file
        """
        try:
            cards = self.get_all_cards()
            
            if not cards:
                logger.warning("No cards to export")
                return
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cards, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(cards)} cards to {filepath}")
        
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise