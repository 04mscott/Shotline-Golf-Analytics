from enum import Enum

class Skill(Enum):
    PGA_TOUR = 'PGA Tour'
    SCRATCH  = 'Scratch'
    HCP_5    = '5 handicap'
    HCP_10   = '10 handicap'
    HCP_15   = '15 handicap'
    HCP_20   = '20 handicap'
    HCP_25   = '25 handicap'

class Lie(Enum):
    TEE = 'Tee'
    FAIRWAY = 'Fairway'
    ROUGH = 'Rough'
    SAND = 'Sand'
    RECOVERY = 'Recovery'
    GREEN = 'Green'
    HOLED = 'Holed'