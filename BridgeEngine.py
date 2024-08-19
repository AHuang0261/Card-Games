from enum import Enum
from typing import Any
from Cards import *
import random
import pygame

class GameState(Enum):
    STARTING = 0
    BIDDING = 1
    PLAYING = 2
    SCORING = 3
    ENDED = 4

class Bid():
    def __init__(self, level, suit):
        self.level = level
        self.suit = suit #follow standard convention w NT being 4

class BridgePlayer(Player):
    pass