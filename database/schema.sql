-- One Piece Card Database Schema

-- Cards table
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT NOT NULL,
    name TEXT NOT NULL,
    card_type TEXT NOT NULL,
    rarity TEXT,
    cost INTEGER,
    attribute TEXT,
    power TEXT,
    counter TEXT,
    color TEXT,
    character_type TEXT,
    effect TEXT,
    trigger_effect TEXT,
    card_set TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(card_id)
);

-- Card Sets table
CREATE TABLE IF NOT EXISTS card_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    release_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(code)
);

-- Colors table
CREATE TABLE IF NOT EXISTS colors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    UNIQUE(name)
);

-- Card Types table
CREATE TABLE IF NOT EXISTS card_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    UNIQUE(name)
);

-- Character Types table
CREATE TABLE IF NOT EXISTS character_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    UNIQUE(name)
);

-- Insert default colors
INSERT OR IGNORE INTO colors (name) VALUES 
    ('Red'),
    ('Green'),
    ('Blue'),
    ('Purple'),
    ('Black'),
    ('Yellow'),
    ('Multicolor');

-- Insert default card types
INSERT OR IGNORE INTO card_types (name) VALUES 
    ('Leader'),
    ('Character'),
    ('Event'),
    ('Stage');

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cards_card_id ON cards(card_id);
CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_color ON cards(color);
CREATE INDEX IF NOT EXISTS idx_cards_card_type ON cards(card_type);
CREATE INDEX IF NOT EXISTS idx_cards_card_set ON cards(card_set);
CREATE INDEX IF NOT EXISTS idx_card_sets_code ON card_sets(code);