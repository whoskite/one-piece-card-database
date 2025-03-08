"""
Data models for One Piece card information.
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Card:
    """Represents a One Piece trading card."""
    card_id: str
    name: str
    card_type: str  # Leader, Character, Event, Stage
    rarity: str
    cost: Optional[int] = None
    attribute: Optional[str] = None
    power: Optional[str] = None
    counter: Optional[str] = None
    color: Optional[str] = None
    character_type: Optional[str] = None  # e.g., "Straw Hat Crew", "Navy", etc.
    effect: Optional[str] = None
    trigger_effect: Optional[str] = None
    card_set: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the card to a dictionary."""
        return {
            'card_id': self.card_id,
            'name': self.name,
            'card_type': self.card_type,
            'rarity': self.rarity,
            'cost': self.cost,
            'attribute': self.attribute,
            'power': self.power,
            'counter': self.counter,
            'color': self.color,
            'character_type': self.character_type,
            'effect': self.effect,
            'trigger_effect': self.trigger_effect,
            'card_set': self.card_set,
            'image_url': self.image_url
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        """Create a Card instance from a dictionary."""
        return cls(
            card_id=data.get('card_id', ''),
            name=data.get('name', ''),
            card_type=data.get('card_type', ''),
            rarity=data.get('rarity', ''),
            cost=data.get('cost'),
            attribute=data.get('attribute'),
            power=data.get('power'),
            counter=data.get('counter'),
            color=data.get('color'),
            character_type=data.get('character_type'),
            effect=data.get('effect'),
            trigger_effect=data.get('trigger_effect'),
            card_set=data.get('card_set'),
            image_url=data.get('image_url')
        )


@dataclass
class CardSet:
    """Represents a collection of One Piece cards."""
    name: str
    code: str
    cards: List[Card]
    release_date: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert the card set to a dictionary."""
        return {
            'name': self.name,
            'code': self.code,
            'release_date': self.release_date,
            'cards': [card.to_dict() for card in self.cards]
        }