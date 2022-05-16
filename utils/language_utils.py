"""Language utils module. Used for various language parsings."""
import re

import nltk


def _get_high_frequency_nouns(text: str) -> list[str]:
    """Get the highest frequency pronouns and nouns in a text string."""
    stop_words = set(nltk.corpus.stopwords.words("english"))
    word_tokens = nltk.word_tokenize(text)
    filtered_sentence = []
    accepted_pos = ["NN", "NNS", "NNP", "NNPS"]  # only want nouns and pronouns

    for (w, p) in nltk.pos_tag(word_tokens):
        if w not in stop_words and p in accepted_pos:
            filtered_sentence.append(w.lower())

    freq = nltk.FreqDist(filtered_sentence)

    return [word for (word, _frequency) in freq.most_common(5)]


def get_important_title_words(title: str, description: str) -> list[str]:
    """Get the most important nouns in the title and description text bodies."""
    high_frequency_description = _get_high_frequency_nouns(description)
    high_frequency_title = _get_high_frequency_nouns(title)
    potential_list = list(
        set(high_frequency_title).intersection(high_frequency_description)
    )
    if len(potential_list) == 0:
        return high_frequency_title[:3]
    else:
        return potential_list


def get_dimensions(description: str) -> dict[str, str | float]:
    """Get the length, width, height and measurement (unit) from a body of text."""
    dimensions_regex = re.search(
        "([\d]+\.?[\d]?[\d]?)\s?(cm|in|mm)?\s?([\*|x|X|\-])?\s?([\d]+\.?[\d]?[\d]?)?\s?(cm|in|mm)?\s?([\*|x|X|\-])?\s?([\d]+\.?[\d]?[\d]?)?\s?(cm|in|mm)",
        description,
        re.IGNORECASE,
    )

    if dimensions_regex:
        length = float(dimensions_regex.group(1))
        width = float(
            0 if dimensions_regex.group(4) is None else dimensions_regex.group(4)
        )
        height = float(
            1 if dimensions_regex.group(7) is None else dimensions_regex.group(7)
        )
        measurement_options = [
            dimensions_regex.group(2),
            dimensions_regex.group(5),
            dimensions_regex.group(8),
            "",
        ]
        measurement = next(match for match in measurement_options if match is not None)

        return {
            "length": length,
            "width": width,
            "height": height,
            "measurement": measurement,
        }

    return {"length": 0.0, "width": 0.0, "height": 0.0, "measurement": "in"}


def get_weight(description: str) -> dict[str, str | float]:
    """Get the weight and measurement (unit) from a body of text."""
    weight_regex = re.search(
        "(Weight|weight).+?([\d]+[\.]?[\d]?[\d]?)\s?(kg|g|lb|oz|pound|ounce)",
        description,
        re.IGNORECASE,
    )
    if weight_regex:
        weight = 0.0 if weight_regex.group(2) is None else float(weight_regex.group(2))
        measurement = weight_regex.group(3)
        return {"weight": weight, "measurement": measurement}

    return {"weight": 0.0, "measurement": "lb"}


def get_unit_discounts(text: str) -> dict[str, float]:
    """Get the discounts applicable for the item when higher quantities ordered."""
    discounts_regex = re.search(
        ".*?([0-9]+)(%)?.*\(([0-9]+) (pieces|lots).*", text, re.IGNORECASE
    )
    if discounts_regex:
        discount = (
            0.0
            if discounts_regex.group(2) != "%" and discounts_regex.group(1) is None
            else (float(discounts_regex.group(1)) / 100)
        )
        discount_amount = (
            0 if discounts_regex.group(3) is None else float(discounts_regex.group(3))
        )
        return {"discount": discount, "discount_amount": discount_amount}

    return {"discount": 0.0, "discount_amount": 0.0}


def get_units_available(text: str) -> int:
    """Get the units available for the paricular item / body of text."""
    available_regex = re.search(".*?([0-9]+).*", text, re.IGNORECASE)
    if available_regex:
        return int(available_regex.group(1))
    else:
        return 0
