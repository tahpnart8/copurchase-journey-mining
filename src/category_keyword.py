"""Keyword-rule categories: RQ1 contrast baseline only, not the official method.

Official categories are the co-purchase communities in src/category.py (see README).
First matching rule wins; rule order is part of the RQ1 result.
"""

import re

import pandas as pd

CATEGORY_RULES = [
    ("CHRISTMAS_SEASONAL", r"CHRISTMAS|XMAS|ADVENT|EASTER|HALLOWEEN|SANTA|SNOWMAN|REINDEER|MISTLETOE"),
    ("PARTY_CELEBRATION",  r"PARTY|BUNTING|BALLOON|BIRTHDAY|WEDDING|CONFETTI|GARLAND|PIÑATA|PINATA"),
    ("BAG_STORAGE",        r"\bBAG\b|LUNCH BOX|LUNCHBOX|JUMBO|SHOPPER|TOTE|BASKET|BOX\b|TIN\b|JAR\b|CRATE|TRUNK|CABINET|DRAWER|HOOK|RACK"),
    ("KITCHEN_DINING",     r"PLATE|BOWL|MUG|CUP\b|TEAPOT|CUTLERY|SPOON|FORK|KNIFE|NAPKIN|JUG|TRAY|COASTER|APRON|OVEN|EGG CUP|BOTTLE|FLASK|TEA TOWEL"),
    ("BAKING_CAKE",        r"CAKE|BAKING|COOKIE|BISCUIT|MUFFIN|CUPCAKE|SWEETHEART|RECIPE|PANTRY"),
    ("LIGHT_CANDLE",       r"CANDLE|T-LIGHT|TEALIGHT|LIGHT\b|LIGHTS|LANTERN|LAMP|TORCH|NIGHTLIGHT"),
    ("JEWELLERY_ACCESSORY", r"NECKLACE|BRACELET|EARRING|RING\b|PENDANT|BROOCH|BEAD|CHARM|SCARF|HAIR|PURSE|WALLET|UMBRELLA|SUNGLASS"),
    ("TOY_GAME",           r"TOY|GAME|PUZZLE|DOLL|BEAR\b|PLAYING CARD|SKIPPING|SPINNING TOP|YO-YO|SOLDIER|DINOSAUR|RATTLE|BALLOON RACE"),
    ("STATIONERY_PAPER",   r"CARD\b|NOTEBOOK|PENCIL|PEN\b|CHALK|STICKER|GIFT WRAP|WRAP\b|TISSUE|PAPER|ENVELOPE|DIARY|JOURNAL|BOOKMARK|ERASER|CRAYON"),
    ("GARDEN_OUTDOOR",     r"GARDEN|PLANT|FLOWER POT|WATERING|BIRD|BEE\b|WIND CHIME|PARASOL|DECK CHAIR|TROWEL|SEED"),
    ("BATH_PERSONAL",      r"SOAP|BATH|TOILET|MIRROR|TOWEL|HOT WATER BOTTLE|PERFUME|HAND WARMER"),
    ("TEXTILE_SOFT",       r"CUSHION|BLANKET|THROW\b|DOORMAT|RUG\b|CURTAIN|TABLECLOTH|PILLOW|QUILT|FELT\b"),
    ("HOME_DECOR",         r"FRAME|HEART|SIGN\b|CLOCK|VASE|ORNAMENT|DECORATION|HANGING|WALL\b|MOBILE|DRAWER KNOB|DOORSTOP|CANDLEHOLDER|HOLDER"),
]
COMPILED_RULES = [(name, re.compile(pattern)) for name, pattern in CATEGORY_RULES]


def assign_category_keyword(description: str) -> str:
    if not isinstance(description, str):
        return "UNKNOWN"
    text = description.upper().strip()
    for name, pattern in COMPILED_RULES:
        if pattern.search(text):
            return name
    return "OTHER"


def assign_category_keyword_series(descriptions: pd.Series) -> pd.Series:
    lookup = {d: assign_category_keyword(d) for d in descriptions.unique()}
    return descriptions.map(lookup)
