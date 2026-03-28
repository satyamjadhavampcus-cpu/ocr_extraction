from difflib import get_close_matches


LABELS = {
    "issued_date": ["issued date", "issue date"],
    "expiry_date": ["expiration date", "expiry date", "expire date"],
    "certificate_number": ["certificate number", "cert number", "certificate no"],
    "naics": ["naics", "naics code", "naics codes"],
    "unspsc": ["unspsc", "unspsc code", "unspsc codes"]
}


def match_label(text):

    text = text.lower()

    for key, values in LABELS.items():
        for value in values:
            match = get_close_matches(value, [text], cutoff=0.75)
            if match:
                return key

    return None
