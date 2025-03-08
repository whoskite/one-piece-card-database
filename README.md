# One Piece Card Database

A web scraper and database for the One Piece Trading Card Game. This project extracts card information from the official One Piece Card Game website and stores it in a structured format for easy access and analysis.

## Features

- Scrapes card data from the official [One Piece Card Game website](https://asia-en.onepiece-cardgame.com/cardlist/)
- Extracts detailed card information including name, ID, cost, attributes, effects, etc.
- Handles pagination to collect all available cards
- Stores data in multiple formats (CSV, JSON, SQLite)
- Includes card image URLs for reference

## Project Structure

```
one-piece-card-database/
├── scraper/
│   ├── __init__.py
│   ├── card_scraper.py     # Main scraping functionality
│   ├── utils.py            # Helper functions
│   └── models.py           # Data models
├── database/
│   ├── __init__.py
│   ├── db_manager.py       # Database operations
│   └── schema.sql          # SQL schema definition
├── data/                   # Output directory for scraped data
├── notebooks/              # Jupyter notebooks for analysis
├── tests/                  # Unit tests
├── requirements.txt        # Project dependencies
├── config.py               # Configuration settings
└── main.py                 # Entry point script
```

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/whoskite/one-piece-card-database.git
   cd one-piece-card-database
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Scraper

To scrape all cards from the website:

```
python main.py --scrape-all
```

To scrape cards with specific filters:

```
python main.py --color Red --card-type Leader
```

### Accessing the Database

The scraped data is stored in multiple formats:

- CSV: `data/one_piece_cards.csv`
- JSON: `data/one_piece_cards.json`
- SQLite: `data/one_piece_cards.db`

You can query the SQLite database directly:

```python
import sqlite3

conn = sqlite3.connect('data/one_piece_cards.db')
cursor = conn.cursor()

# Example: Get all Red cards
cursor.execute("SELECT * FROM cards WHERE color = 'Red'")
red_cards = cursor.fetchall()

# Example: Get all Leader cards
cursor.execute("SELECT * FROM cards WHERE card_type = 'Leader'")
leader_cards = cursor.fetchall()

conn.close()
```

## Ethical Considerations

This project is designed for personal use and educational purposes. Please be respectful when scraping the website:

- Add delays between requests to avoid overloading the server
- Use proper user-agent headers to identify your scraper
- Respect the website's terms of service
- Do not distribute copyrighted images or data commercially

## Legal Notice

The One Piece Card Game and all card images and data are copyrighted by Bandai and Eiichiro Oda/Shueisha. This project is not affiliated with or endorsed by these entities.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.