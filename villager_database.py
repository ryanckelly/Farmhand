"""
Villager Database for Stardew Valley Companion System

Master list of all trackable villagers with metadata including:
- Display colors for UI chip bar
- Category classification
- Maximum heart levels
- Initials for colored circle avatars
"""

from enum import Enum
from typing import TypedDict


class VillagerCategory(Enum):
    """Villager classification types."""
    MARRIAGEABLE = "marriageable"  # Can be married
    TOWNSPERSON = "townsperson"     # Regular NPCs
    SPECIAL = "special"              # Wizard, Krobus, Dwarf


class VillagerData(TypedDict):
    """Type definition for villager metadata."""
    category: VillagerCategory
    color: str  # Hex color for UI
    initials: str  # 2-letter abbreviation for avatar
    max_hearts: int  # 10 for most, 14 for spouse


# Complete villager database - 32 villagers
VILLAGERS: dict[str, VillagerData] = {
    # Marriageable villagers (12) - max 14 hearts when married
    "Abigail": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#9b59b6",  # Purple
        "initials": "AB",
        "max_hearts": 14
    },
    "Alex": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#3498db",  # Blue
        "initials": "AL",
        "max_hearts": 14
    },
    "Elliott": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#e74c3c",  # Red
        "initials": "EL",
        "max_hearts": 14
    },
    "Emily": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#ff1493",  # Hot pink
        "initials": "EM",
        "max_hearts": 14
    },
    "Haley": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#f39c12",  # Orange
        "initials": "HA",
        "max_hearts": 14
    },
    "Harvey": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#16a085",  # Teal
        "initials": "HV",
        "max_hearts": 14
    },
    "Leah": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#27ae60",  # Green
        "initials": "LE",
        "max_hearts": 14
    },
    "Maru": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#8e44ad",  # Purple violet
        "initials": "MA",
        "max_hearts": 14
    },
    "Penny": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#e67e22",  # Carrot orange
        "initials": "PE",
        "max_hearts": 14
    },
    "Sam": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#f1c40f",  # Yellow
        "initials": "SA",
        "max_hearts": 14
    },
    "Sebastian": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#34495e",  # Dark slate
        "initials": "SE",
        "max_hearts": 14
    },
    "Shane": {
        "category": VillagerCategory.MARRIAGEABLE,
        "color": "#95a5a6",  # Light gray
        "initials": "SH",
        "max_hearts": 14
    },

    # Townspeople (17) - max 10 hearts
    "Caroline": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#2ecc71",  # Emerald
        "initials": "CA",
        "max_hearts": 10
    },
    "Clint": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#7f8c8d",  # Gray
        "initials": "CL",
        "max_hearts": 10
    },
    "Demetrius": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#1abc9c",  # Turquoise
        "initials": "DE",
        "max_hearts": 10
    },
    "Evelyn": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#ecf0f1",  # Light silver
        "initials": "EV",
        "max_hearts": 10
    },
    "George": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#bdc3c7",  # Silver
        "initials": "GE",
        "max_hearts": 10
    },
    "Gus": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#d35400",  # Pumpkin
        "initials": "GU",
        "max_hearts": 10
    },
    "Jas": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#ff69b4",  # Light pink
        "initials": "JA",
        "max_hearts": 10
    },
    "Jodi": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#ff6347",  # Tomato
        "initials": "JO",
        "max_hearts": 10
    },
    "Kent": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#556b2f",  # Olive
        "initials": "KE",
        "max_hearts": 10
    },
    "Lewis": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#8b4513",  # Saddle brown
        "initials": "LW",
        "max_hearts": 10
    },
    "Linus": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#228b22",  # Forest green
        "initials": "LI",
        "max_hearts": 10
    },
    "Marnie": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#cd853f",  # Peru
        "initials": "MN",
        "max_hearts": 10
    },
    "Pam": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#daa520",  # Goldenrod
        "initials": "PM",
        "max_hearts": 10
    },
    "Pierre": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#32cd32",  # Lime green
        "initials": "PI",
        "max_hearts": 10
    },
    "Robin": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#ff4500",  # Orange red
        "initials": "RO",
        "max_hearts": 10
    },
    "Vincent": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#87ceeb",  # Sky blue
        "initials": "VI",
        "max_hearts": 10
    },
    "Willy": {
        "category": VillagerCategory.TOWNSPERSON,
        "color": "#4682b4",  # Steel blue
        "initials": "WI",
        "max_hearts": 10
    },

    # Special NPCs (3) - max 10 hearts
    "Dwarf": {
        "category": VillagerCategory.SPECIAL,
        "color": "#696969",  # Dim gray
        "initials": "DW",
        "max_hearts": 10
    },
    "Krobus": {
        "category": VillagerCategory.SPECIAL,
        "color": "#4b0082",  # Indigo
        "initials": "KR",
        "max_hearts": 10
    },
    "Wizard": {
        "category": VillagerCategory.SPECIAL,
        "color": "#9370db",  # Medium purple
        "initials": "WZ",
        "max_hearts": 10
    },
}


def get_all_villagers() -> list[str]:
    """Return list of all villager names alphabetically."""
    return sorted(VILLAGERS.keys())


def get_villager_by_category(category: VillagerCategory) -> list[str]:
    """Return villagers filtered by category."""
    return sorted([
        name for name, data in VILLAGERS.items()
        if data["category"] == category
    ])


def get_marriageable_villagers() -> list[str]:
    """Return only marriageable villagers (12 total)."""
    return get_villager_by_category(VillagerCategory.MARRIAGEABLE)


def get_villager_color(name: str) -> str:
    """Get hex color for a villager. Returns green if not found."""
    return VILLAGERS.get(name, {}).get("color", "#00ff00")


def get_villager_initials(name: str) -> str:
    """Get 2-letter initials for a villager. Returns first 2 letters if not found."""
    return VILLAGERS.get(name, {}).get("initials", name[:2].upper())


def get_villager_max_hearts(name: str) -> int:
    """Get maximum heart level for a villager. Returns 10 as default."""
    return VILLAGERS.get(name, {}).get("max_hearts", 10)


# Quick validation
if __name__ == "__main__":
    print(f"Total villagers: {len(VILLAGERS)}")
    print(f"Marriageable: {len(get_marriageable_villagers())}")
    print(f"Townspeople: {len(get_villager_by_category(VillagerCategory.TOWNSPERSON))}")
    print(f"Special: {len(get_villager_by_category(VillagerCategory.SPECIAL))}")
    print("\nAll villagers:")
    for name in get_all_villagers():
        color = get_villager_color(name)
        initials = get_villager_initials(name)
        print(f"  {name:12} {initials:4} {color}")
