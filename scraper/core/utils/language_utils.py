import nltk
import re
from textblob import TextBlob
from IPython import embed

class LanguageUtils(object):
  @staticmethod
  def get_important_title_words(title, description):
    high_frequency_description = LanguageUtils().get_high_frequency_nouns(description)
    high_frequency_title = LanguageUtils().get_high_frequency_nouns(title)
    potential_list = list(set(high_frequency_title).intersection(high_frequency_description))
    if len(potential_list) == 0:
      return high_frequency_title[:3]
    else: 
      return potential_list

  @staticmethod
  def get_high_frequency_nouns(text):
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.word_tokenize(text)
    filtered_sentence = []
    accepted_pos = ["NN", "NNS", "NNP", "NNPS"] # only want nouns and pronouns

    for (w,p) in nltk.pos_tag(word_tokens):
      if w not in stop_words and p in accepted_pos:
        filtered_sentence.append(w.lower())

    freq = nltk.FreqDist(filtered_sentence)

    return [word for (word, _frequency) in freq.most_common(5)]

  @staticmethod
  def get_dimensions(description):
    dimensions_regex = re.search('.([\d\.]+)\s?[(\*|x|X)]\s?([\d\.]+)\s?[(\*|x|X)]?\s?([\d\.]+)?\s?([cm|in|mm]+)*', description, re.IGNORECASE)
    if dimensions_regex:
      length = float(dimensions_regex.group(1))
      width = float(dimensions_regex.group(2))
      height = float(0 if dimensions_regex.group(3) is None else dimensions_regex.group(3))
      measurement = dimensions_regex.group(4)
      return {"length": length, "width": width, "height": height, "measurement": measurement}


