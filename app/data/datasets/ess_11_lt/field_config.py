"""
ESS Round 11 – Lithuania subset
Field configuration: which variables define the persona vs. which are questions.
"""

from pathlib import Path

# paths
_THIS_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = (
    _THIS_DIR.parent.parent # → data/
    / "raw_data"
    / "Europos socialinio tyrimo 11-osios bangos Lietuvoje duomenys 2024"
    / "FROM_ESS"
)
CODEBOOK_HTML = RAW_DATA_DIR / "ESS11e04_1-subset codebook.html"
RAW_CSV       = RAW_DATA_DIR / "ESS11e04_1-subset.csv"
OUTPUT_DIR    = _THIS_DIR

# persona fields
PERSONA_FIELDS: list[str] = [
    "gndr",       # Gender
    "agea",       # Age of respondent (calculated)
    "edlvdlt",    # Highest level of education, Lithuania
    "domicil",    # Domicile – Which phrase on this card best describes the area where you live?
    "region",     # region code
    "rlgblg",     # religion - Do you consider yourself as belonging to any particular religion or denomination?
    "rlgdgr",     # How religious are you (0-10)
    "lrscale",    # Placement on left-right scale (0-10)
    "polintr",    # How interested in politics (very interest -> not at all interested + don't know + refused + no answer)
    "vote",       # Voted in last national election (yes,no, not eligible, don't know + refused + no answer)
]

# question fields
QUESTION_FIELDS: list[str] = [
    "gincdif",    # Government should reduce differences in income levels
    "freehms",    # Gays and lesbians free to live life as they wish
    "stflife",    # How satisfied with life as a whole (0-10)
    "happy",      # How happy are you (0-10)
    "imsmetn",    # Allow many/few immigrants of same race/ethnic group
    "imdfetn",    # Allow many/few immigrants of different race/ethnic group
    "impcntr",    # Allow many/few immigrants from poorer countries outside Europe
    "trstprl",    # Trust in country's parliament (0-10)
    "trstlgl",    # Trust in the legal system (0-10)
    "trstplc",    # Trust in the police (0-10)
    "trstplt",    # Trust in politicians (0-10)
    "stfeco",     # How satisfied with present state of economy (0-10)
    "stfgov",     # How satisfied with the national government (0-10)
    "stfdem",     # How satisfied with the way democracy works (0-10)
    "stfedu",     # State of education in country nowadays (0-10)
    "stfhlth",    # State of health services in country nowadays (0-10)
]

# respondent-id column in the raw CSV
SOURCE_ID_COLUMN = "idno"
