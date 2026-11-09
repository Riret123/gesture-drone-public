"""Exact bilingual text commands; no microphone or speech-to-text dependency."""
import unicodedata

PHRASES = {
    'take off': 'open_palm', 'takeoff': 'open_palm', 'взлет': 'open_palm',
    'land': 'land', 'посадка': 'land', 'садись': 'land',
    'hold': 'hold', 'зависни': 'hold', 'стой': 'hold',
    'emergency land': 'emergency', 'аварийная посадка': 'emergency',
}


def parse(text: str) -> str | None:
    normalized = ' '.join(unicodedata.normalize('NFKC', text).casefold().replace('ё', 'е').split())
    return PHRASES.get(normalized)
