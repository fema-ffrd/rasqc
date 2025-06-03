from enum import Enum


class ColorTheme(Enum):
    ARCADE = {
        "background": "rgb(50, 50, 50)",
        "heading1": "rgb(20, 180, 160)",
        "heading2": "rgb(140, 140, 255)",
        "body": "rgb(170, 170, 170)",
        "shadow": "rgb(100, 100, 100)",
    }
    ADAMS = {
        "background": "rgb(82, 94, 100)",
        "heading1": "rgb(100, 60, 30)",
        "heading2": "rgb(60, 60, 60)",
        "body": "rgb(170, 170, 170)",
        "shadow": "rgb(100, 100, 100)",
    }
    ARCTIC = {
        "background": "rgb(255, 255, 255)",
        "heading1": "rgb(0, 220, 200)",
        "heading2": "rgb(200, 200, 240)",
        "body": "rgb(160, 180, 200)",
        "shadow": "rgb(0, 220, 200)",
    }
