"""
Pet Data Module
Contains experience requirements for pet leveling
"""

# Experience table: level -> (exp_to_next_level, accumulated_exp)
# accumulated_exp is the TOTAL exp needed to REACH that level from level 1
PET_EXP_TABLE = {
    1: {"exp_to_next": 1500, "accumulated": 0},
    2: {"exp_to_next": 4500, "accumulated": 1500},
    3: {"exp_to_next": 7500, "accumulated": 6000},
    4: {"exp_to_next": 10500, "accumulated": 13500},
    5: {"exp_to_next": 13500, "accumulated": 24000},
    6: {"exp_to_next": 16500, "accumulated": 37500},
    7: {"exp_to_next": 19500, "accumulated": 54000},
    8: {"exp_to_next": 27540, "accumulated": 73500},
    9: {"exp_to_next": 37305, "accumulated": 101040},
    10: {"exp_to_next": 49500, "accumulated": 138345},
    11: {"exp_to_next": 78450, "accumulated": 187845},
    12: {"exp_to_next": 133725, "accumulated": 266295},
    13: {"exp_to_next": 187650, "accumulated": 400020},
    14: {"exp_to_next": 240300, "accumulated": 587670},
    15: {"exp_to_next": 291600, "accumulated": 827970},
    16: {"exp_to_next": 341775, "accumulated": 1119570},
    17: {"exp_to_next": 390675, "accumulated": 1461345},
    18: {"exp_to_next": 438375, "accumulated": 1852020},
    19: {"exp_to_next": 485025, "accumulated": 2290395},
    20: {"exp_to_next": 530550, "accumulated": 2775420},
    21: {"exp_to_next": 575025, "accumulated": 3305970},
    22: {"exp_to_next": 618450, "accumulated": 3880995},
    23: {"exp_to_next": 660900, "accumulated": 4499445},
    24: {"exp_to_next": 702450, "accumulated": 5160345},
    25: {"exp_to_next": 743025, "accumulated": 5862795},
    26: {"exp_to_next": 782775, "accumulated": 6605820},
    27: {"exp_to_next": 821625, "accumulated": 7388595},
    28: {"exp_to_next": 859725, "accumulated": 8210220},
    29: {"exp_to_next": 897075, "accumulated": 9069945},
    30: {"exp_to_next": 933675, "accumulated": 9967020},
    31: {"exp_to_next": 969525, "accumulated": 10900695},
    32: {"exp_to_next": 1004775, "accumulated": 11870220},
    33: {"exp_to_next": 1039425, "accumulated": 12874995},
    34: {"exp_to_next": 1073475, "accumulated": 13914420},
    35: {"exp_to_next": 1106925, "accumulated": 14987895},
    36: {"exp_to_next": 1139925, "accumulated": 16094820},
    37: {"exp_to_next": 1172400, "accumulated": 17234745},
    38: {"exp_to_next": 1204425, "accumulated": 18407145},
    39: {"exp_to_next": 1236075, "accumulated": 19611570},
    40: {"exp_to_next": 1267425, "accumulated": 20847645},
    41: {"exp_to_next": 1298325, "accumulated": 22115070},
    42: {"exp_to_next": 1329000, "accumulated": 23413395},
    43: {"exp_to_next": 1359375, "accumulated": 24742395},
    44: {"exp_to_next": 1389600, "accumulated": 26101770},
    45: {"exp_to_next": 1419525, "accumulated": 27491370},
    46: {"exp_to_next": 1449375, "accumulated": 28910895},
    47: {"exp_to_next": 1479075, "accumulated": 30360270},
    48: {"exp_to_next": 1508775, "accumulated": 31839345},
    49: {"exp_to_next": 1538325, "accumulated": 33348120},
    50: {"exp_to_next": 1567950, "accumulated": 34886445},
    51: {"exp_to_next": 1597575, "accumulated": 36454395},
    52: {"exp_to_next": 1627200, "accumulated": 38051970},
    53: {"exp_to_next": 1657050, "accumulated": 39679170},
    54: {"exp_to_next": 1686975, "accumulated": 41336220},
    55: {"exp_to_next": 1717050, "accumulated": 43023195},
    56: {"exp_to_next": 1747350, "accumulated": 44740245},
    57: {"exp_to_next": 1777875, "accumulated": 46487595},
    58: {"exp_to_next": 1808775, "accumulated": 48265470},
    59: {"exp_to_next": 1839900, "accumulated": 50074245},
    60: {"exp_to_next": 1871400, "accumulated": 51914145},
    61: {"exp_to_next": 1903350, "accumulated": 53785545},
    62: {"exp_to_next": 1935675, "accumulated": 55688895},
    63: {"exp_to_next": 1968450, "accumulated": 57624570},
    64: {"exp_to_next": 2001750, "accumulated": 59593020},
    65: {"exp_to_next": 2035575, "accumulated": 61594770},
    66: {"exp_to_next": 2070000, "accumulated": 63630345},
    67: {"exp_to_next": 2105025, "accumulated": 65700345},
    68: {"exp_to_next": 2140650, "accumulated": 67805370},
    69: {"exp_to_next": 2177025, "accumulated": 69946020},
    70: {"exp_to_next": 2214075, "accumulated": 72123045},
    71: {"exp_to_next": 2251875, "accumulated": 74337120},
    72: {"exp_to_next": 2290500, "accumulated": 76588995},
    73: {"exp_to_next": 2329875, "accumulated": 78879495},
    74: {"exp_to_next": 2370150, "accumulated": 81209370},
    75: {"exp_to_next": 2411400, "accumulated": 83579520},
    76: {"exp_to_next": 2453475, "accumulated": 85990920},
    77: {"exp_to_next": 2496600, "accumulated": 88444395},
    78: {"exp_to_next": 2540700, "accumulated": 90940995},
    79: {"exp_to_next": 2585775, "accumulated": 93481695},
    80: {"exp_to_next": 2632050, "accumulated": 96067470},
    81: {"exp_to_next": 2679375, "accumulated": 98699520},
    82: {"exp_to_next": 2727825, "accumulated": 101378895},
    83: {"exp_to_next": 2777550, "accumulated": 104106720},
    84: {"exp_to_next": 2828400, "accumulated": 106884270},
    85: {"exp_to_next": 2880525, "accumulated": 109712670},
    86: {"exp_to_next": 2934000, "accumulated": 112593195},
    87: {"exp_to_next": 2988825, "accumulated": 115527195},
    88: {"exp_to_next": 3044925, "accumulated": 118516020},
    89: {"exp_to_next": 3102525, "accumulated": 121560945},
    90: {"exp_to_next": 3161475, "accumulated": 124663470},
    91: {"exp_to_next": 3222000, "accumulated": 127824945},
    92: {"exp_to_next": 3283950, "accumulated": 131046945},
    93: {"exp_to_next": 3347475, "accumulated": 134330895},
    94: {"exp_to_next": 3412575, "accumulated": 137678370},
    95: {"exp_to_next": 3479325, "accumulated": 141090945},
    96: {"exp_to_next": 3547725, "accumulated": 144570270},
    97: {"exp_to_next": 3617850, "accumulated": 148117995},
    98: {"exp_to_next": 3689625, "accumulated": 151735845},
    99: {"exp_to_next": 3763275, "accumulated": 155425470},
    100: {"exp_to_next": 3838650, "accumulated": 159188745},
    101: {"exp_to_next": 3915900, "accumulated": 163027395},
    102: {"exp_to_next": 3994950, "accumulated": 166943295},
    103: {"exp_to_next": 4076025, "accumulated": 170938245},
    104: {"exp_to_next": 4158975, "accumulated": 175014270},
    105: {"exp_to_next": 4243875, "accumulated": 179173245},
    106: {"exp_to_next": 4330875, "accumulated": 183417120},
    107: {"exp_to_next": 4419900, "accumulated": 187747995},
    108: {"exp_to_next": 4511025, "accumulated": 192167895},
    109: {"exp_to_next": 4604250, "accumulated": 196678920},
    110: {"exp_to_next": 4699650, "accumulated": 201283170},
    111: {"exp_to_next": 4797225, "accumulated": 205982820},
    112: {"exp_to_next": 4897125, "accumulated": 210780045},
    113: {"exp_to_next": 4999200, "accumulated": 215677170},
    114: {"exp_to_next": 5103600, "accumulated": 220676370},
    115: {"exp_to_next": 5210400, "accumulated": 225779970},
    116: {"exp_to_next": 5319525, "accumulated": 230990370},
    117: {"exp_to_next": 5431125, "accumulated": 236309895},
    118: {"exp_to_next": 5545125, "accumulated": 241741020},
    119: {"exp_to_next": 5661675, "accumulated": 247286145},
    120: {"exp_to_next": 0, "accumulated": 252947820},  # Max level
}


def get_exp_for_level(target_level):
    """
    Get the accumulated experience needed to reach a target level.
    
    Args:
        target_level (int): The level you want to reach (2-120)
    
    Returns:
        int: Total accumulated EXP needed to reach that level from level 1
    """
    if target_level < 1 or target_level > 120:
        return 0
    return PET_EXP_TABLE.get(target_level, {}).get("accumulated", 0)


def get_levels_from_exp(current_level, current_exp, target_level):
    """
    Calculate how many level-ups are needed to reach target level.
    
    Args:
        current_level (int): Current pet level
        current_exp (int): Current accumulated EXP
        target_level (int): Target level to reach
    
    Returns:
        int: Number of level-ups needed (for UPGRADE_CLICKS)
    """
    if current_level >= target_level:
        return 0
    return target_level - current_level


def is_pet_ready_for_level(current_exp, target_level):
    """
    Check if a pet has enough EXP to reach the target level.
    
    Args:
        current_exp (int): Pet's current accumulated EXP
        target_level (int): Target level to check against
    
    Returns:
        bool: True if pet has enough EXP to reach target level
    """
    required_exp = get_exp_for_level(target_level)
    return current_exp >= required_exp
