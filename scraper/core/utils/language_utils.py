import nltk
import re

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
    dimensions_regex = re.search('([\d]+\.?[\d]?[\d]?)\s?(cm|in|mm)?\s?([\*|x|X|\-])?\s?([\d]+\.?[\d]?[\d]?)?\s?(cm|in|mm)?\s?([\*|x|X|\-])?\s?([\d]+\.?[\d]?[\d]?)?\s?(cm|in|mm)', description, re.IGNORECASE)
    if dimensions_regex:
      length = float(dimensions_regex.group(1))
      width = float(0 if dimensions_regex.group(4) is None else dimensions_regex.group(4))
      height = float(1 if dimensions_regex.group(7) is None else dimensions_regex.group(7))
      measurement_options = [dimensions_regex.group(2), dimensions_regex.group(5), dimensions_regex.group(8), ""]
      measurement = next(match for match in measurement_options if match is not None)
      return {"length": length, "width": width, "height": height, "measurement": measurement}
  
  @staticmethod
  def get_weight_or_material(description):
    weight_regex = re.search('(Weight|weight).+?([\d]+[\.]?[\d]?[\d]?)\s?(kg|g|lb)', description, re.IGNORECASE)
    if weight_regex:
      weight = None if weight_regex.group(2) is None else float(weight_regex.group(2))
      measurement = weight_regex.group(3)
      return {"weight": weight, "measurement": measurement, "material": None}
    
    material_regex = re.search('(wood|steel|plastic|fabric|polyester)', description, re.IGNORECASE)
    if material_regex:
      return {"weight": None, "measurement": None, "material": material_regex.group(1)} # may need to search for most common grouping, but works for now

    return {"weight": None, "measurement": None, "material": None} 
  
  @staticmethod
  def get_unit_discounts(text):
    discounts_regex = re.search('.*?([0-9]+)(%)?.*\(([0-9]+) (pieces|lots).*', text, re.IGNORECASE)
    if discounts_regex:
      discount = 0.0 if discounts_regex.group(2) != "%" and discounts_regex.group(1) == None else (float(discounts_regex.group(1)) / 100)
      discount_amount = 0 if discounts_regex.group(3) == None else int(discounts_regex.group(3))
      return {"discount": discount, "discount_amount": discount_amount}

  @staticmethod
  def get_units_available(text):
    available_regex = re.search('.*?([0-9]+).*', text, re.IGNORECASE)
    if available_regex:
      return int(available_regex.group(1))
    else:
      return 0
