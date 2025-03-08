#!/usr/bin/env python3
"""
One Piece Card Database - Main Entry Point

This script provides a command-line interface for scraping and managing
the One Piece Card Game database.
"""
import os
import argparse
import logging
import sys
from typing import List, Optional

from scraper.card_scraper import OnePieceCardScraper
from database.db_manager import DatabaseManager
from scraper.utils import ensure_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("one_piece_card_database.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="One Piece Card Database Tool")
    
    # Scraping options
    scraping_group = parser.add_argument_group("Scraping Options")
    scraping_group.add_argument("--scrape-all", action="store_true", help="Scrape all cards")
    scraping_group.add_argument("--color", type=str, help="Filter cards by color")
    scraping_group.add_argument("--card-type", type=str, help="Filter cards by type")
    scraping_group.add_argument("--max-pages", type=int, help="Maximum number of pages to scrape")
    scraping_group.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    
    # Database options
    db_group = parser.add_argument_group("Database Options")
    db_group.add_argument("--init-db", action="store_true", help="Initialize the database")
    db_group.add_argument("--db-path", type=str, default="data/one_piece_cards.db", help="Path to the database file")
    
    # Export options
    export_group = parser.add_argument_group("Export Options")
    export_group.add_argument("--export-csv", action="store_true", help="Export database to CSV")
    export_group.add_argument("--export-json", action="store_true", help="Export database to JSON")
    export_group.add_argument("--output-dir", type=str, default="data", help="Directory to save output files")
    
    # Query options
    query_group = parser.add_argument_group("Query Options")
    query_group.add_argument("--list-colors", action="store_true", help="List all card colors")
    query_group.add_argument("--list-types", action="store_true", help="List all card types")
    query_group.add_argument("--list-sets", action="store_true", help="List all card sets")
    query_group.add_argument("--get-by-color", type=str, help="Get cards by color")
    query_group.add_argument("--get-by-type", type=str, help="Get cards by type")
    query_group.add_argument("--get-by-set", type=str, help="Get cards by set code")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Create output directory if it doesn't exist
    ensure_directory(args.output_dir)
    
    # Initialize database if requested
    if args.init_db:
        logger.info("Initializing database...")
        db_manager = DatabaseManager(args.db_path)
        db_manager.initialize_database()
        logger.info("Database initialized successfully")
    
    # Scrape cards if requested
    if args.scrape_all or args.color or args.card_type:
        logger.info("Starting card scraper...")
        scraper = OnePieceCardScraper(headless=args.headless, output_dir=args.output_dir)
        
        try:
            if args.color or args.card_type:
                logger.info(f"Scraping cards with filters: color={args.color}, type={args.card_type}")
                cards = scraper.scrape_with_filters(color=args.color, card_type=args.card_type)
            else:
                logger.info("Scraping all cards...")
                cards = scraper.scrape_all_cards(max_pages=args.max_pages)
            
            # Save scraped data
            if cards:
                logger.info(f"Scraped {len(cards)} cards")
                
                # Save to CSV
                csv_path = scraper.save_to_csv()
                logger.info(f"Saved cards to CSV: {csv_path}")
                
                # Save to JSON
                json_path = scraper.save_to_json()
                logger.info(f"Saved cards to JSON: {json_path}")
                
                # Save to database
                logger.info("Saving cards to database...")
                db_manager = DatabaseManager(args.db_path)
                inserted_count = db_manager.insert_cards(cards)
                logger.info(f"Inserted {inserted_count} new cards into the database")
            else:
                logger.warning("No cards were scraped")
        
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return 1
    
    # Export database if requested
    if args.export_csv or args.export_json:
        db_manager = DatabaseManager(args.db_path)
        
        if args.export_csv:
            csv_path = os.path.join(args.output_dir, "one_piece_cards_export.csv")
            logger.info(f"Exporting database to CSV: {csv_path}")
            db_manager.export_to_csv(csv_path)
        
        if args.export_json:
            json_path = os.path.join(args.output_dir, "one_piece_cards_export.json")
            logger.info(f"Exporting database to JSON: {json_path}")
            db_manager.export_to_json(json_path)
    
    # Handle query options
    if args.list_colors or args.list_types or args.list_sets or args.get_by_color or args.get_by_type or args.get_by_set:
        db_manager = DatabaseManager(args.db_path)
        
        try:
            db_manager.connect()
            
            if args.list_colors:
                db_manager.cursor.execute("SELECT name FROM colors ORDER BY name")
                colors = [row['name'] for row in db_manager.cursor.fetchall()]
                print("\nAvailable Colors:")
                for color in colors:
                    print(f"- {color}")
            
            if args.list_types:
                db_manager.cursor.execute("SELECT name FROM card_types ORDER BY name")
                types = [row['name'] for row in db_manager.cursor.fetchall()]
                print("\nAvailable Card Types:")
                for card_type in types:
                    print(f"- {card_type}")
            
            if args.list_sets:
                db_manager.cursor.execute("SELECT code, name FROM card_sets ORDER BY code")
                sets = [(row['code'], row['name']) for row in db_manager.cursor.fetchall()]
                print("\nAvailable Card Sets:")
                for code, name in sets:
                    print(f"- {code}: {name}")
            
            if args.get_by_color:
                cards = db_manager.get_cards_by_color(args.get_by_color)
                print(f"\nCards with color '{args.get_by_color}': {len(cards)}")
                for card in cards[:10]:  # Show only first 10 cards
                    print(f"- {card['card_id']}: {card['name']} ({card['card_type']})")
                if len(cards) > 10:
                    print(f"... and {len(cards) - 10} more")
            
            if args.get_by_type:
                cards = db_manager.get_cards_by_type(args.get_by_type)
                print(f"\nCards with type '{args.get_by_type}': {len(cards)}")
                for card in cards[:10]:  # Show only first 10 cards
                    print(f"- {card['card_id']}: {card['name']} ({card['color']})")
                if len(cards) > 10:
                    print(f"... and {len(cards) - 10} more")
            
            if args.get_by_set:
                cards = db_manager.get_cards_by_set(args.get_by_set)
                print(f"\nCards in set '{args.get_by_set}': {len(cards)}")
                for card in cards[:10]:  # Show only first 10 cards
                    print(f"- {card['card_id']}: {card['name']} ({card['color']} {card['card_type']})")
                if len(cards) > 10:
                    print(f"... and {len(cards) - 10} more")
        
        finally:
            db_manager.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())