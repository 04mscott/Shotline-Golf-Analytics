from enum import StrEnum

class Skill(StrEnum):
    PGA_TOUR = 'pga tour'
    SCRATCH  = 'scratch'
    HCP_5    = '5 handicap'
    HCP_10   = '10 handicap'
    HCP_15   = '15 handicap'
    HCP_20   = '20 handicap'
    HCP_25   = '25 handicap'

class Lie(StrEnum):
    TEE = 'tee'
    FAIRWAY = 'fairway'
    ROUGH = 'rough'
    SAND = 'sand'
    RECOVERY = 'recovery'
    GREEN = 'green'
    HOLED = 'holed'