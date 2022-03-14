"""A util file used for installing the necessary nltk resources."""
import nltk


def download_nltk_resources():
    """Install necessary nltk packages used for language utils."""
    nltk.download("stopwords")
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
