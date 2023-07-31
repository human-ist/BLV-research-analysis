from typing import List
import re
from io import StringIO
import nltk
# Following dependencies must be installed.
#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('universal_tagset')
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag


class TokenUtils:
  """
  Utility class to perform text analysis at token level.
  """

  ENGLISH_STOPWORDS = set(stopwords.words('english'))
  BETWEEN_PAR_PATTERN:str = '[\(\[].*?[\)\]]' # To exclude acronyms e.g. (PVI)
  INCLUDED_POS: List[str] = ['ADP', 'CONJ', 'DET', 'NUM', 'PRT', 'PRON']
  EXCLUDED_POS: List[str] = ['ADP', 'CONJ', 'DET', 'NUM', 'PRT', 'PRON', 'VERB', '.']

  # string.punctuation: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
  SENTENCE_SEPARATOR_PUNCT:set = set((punct) for punct in ['!', ',', '.', ':', ';', '?'])


  @staticmethod
  def tokenize(text:str) -> List[List[str]]:
    """
    Tokenize text by sentence, then by words, then filter according to POS.
    Example value: "It Feels Like Taking a Gamble": Exploring Perceptions, Practices, and Challenges of Using Makeup and Cosmetics for People with Visual Impairments
    """
    sentences_arr = []
    for sentence in sent_tokenize(text):
      sentence_arr = []
      words = word_tokenize(sentence)
      for word, pos in pos_tag(words, tagset='universal'):
        if not TokenUtils.filter(word, pos): # TODO can be parametrized
          sentence_arr.append(word.lower())
      sentences_arr.append(sentence_arr)
    return sentences_arr


  @staticmethod
  def keywords_tokenize(keywords_row:str) -> List[str]:
    """
    keywords_row: 'Color to gray; probabilistic graphical model; visual cue.'
    """
    auth_keywords_list = keywords_row.lower().split('; ')

    cleaned_keywords = []
    for i in range(0, len(auth_keywords_list)):
      keyword = auth_keywords_list[i]
      keyword = keyword.replace('-', ' ').replace('.', '')
      # Remove between (), terms are acronyms
      keyword = re.sub("[\(\[].*?[\)\]]", "", keyword)
      keyword = keyword.strip()
      cleaned_keywords.append(keyword)
      # Add the keywords separator
      if i+1 < len(auth_keywords_list):
        cleaned_keywords.append(';')

    return cleaned_keywords


  # TODO remove e.g., i.e.

  @staticmethod
  def filter(token:str, pos:str) -> str:
    """
    POS tagging (tagset='universal'):
      ADJ 	adjective 	new, good, high, special, big, local
      ADP 	adposition 	on, of, at, with, by, into, under
      ADV 	adverb 	really, already, still, early, now
      CONJ 	conjunction 	and, or, but, if, while, although
      DET 	determiner, article 	the, a, some, most, every, no, which
      NOUN 	noun 	year, home, costs, time, Africa
      NUM 	numeral 	twenty-four, fourth, 1991, 14:24
      PRT 	particle 	at, on, out, over per, that, up, with
      PRON 	pronoun 	he, their, her, its, my, I, us
      VERB 	verb 	is, say, told, given, playing, would
      . 	punctuation marks 	. , ; !
      X 	other 	ersatz, esprit, dunno, gr8, univeristy
    Source:
    - https://www.nltk.org/api/nltk.tokenize.html
    - https://www.nltk.org/api/nltk.tag.pos_tag.html; https://www.nltk.org/book/ch05.html
    """
    # Only check length for non punctuation POS

    # Short token
    if (pos != '.' and len(token) < 2):
      return True

    # Irrelevant part of speech
    if pos in TokenUtils.INCLUDED_POS:
      return True

    # Irrelevant punctuation
    if pos == '.' and not token in TokenUtils.SENTENCE_SEPARATOR_PUNCT:
      return True

    # Is a stopword
    if token in TokenUtils.ENGLISH_STOPWORDS:
      return True

    # Is an acronym
    if re.search(TokenUtils.BETWEEN_PAR_PATTERN, token):
      return True

    # TODO is an e.g. i.e. -> stopword in calculation?

    return False


  @staticmethod
  def flatten(tokens: List[List[str]]) -> List[str]:
    """
    Flatten a two dimensional data structure to one dimension.
    """
    flattened_tokens = []
    for sentence in tokens:
      for word in sentence:
        flattened_tokens.append(word)
    return flattened_tokens


  @staticmethod
  def join(tokens: List[str]) -> str:
    nb_tokens = len(tokens)
    buffer = StringIO()
    for i in range(0, nb_tokens):
      buffer.write(tokens[i])
      # Add space if the next token is not a punctuation
      if i+1 < nb_tokens and tokens[i+1] not in TokenUtils.SENTENCE_SEPARATOR_PUNCT:
        buffer.write(' ')
    return buffer.getvalue()


  @staticmethod
  def filter_old(token:str, pos:str = None) -> str:
    """
    POS tagging (tagset='universal'):
      ADJ 	adjective 	new, good, high, special, big, local
      ADP 	adposition 	on, of, at, with, by, into, under
      ADV 	adverb 	really, already, still, early, now
      CONJ 	conjunction 	and, or, but, if, while, although
      DET 	determiner, article 	the, a, some, most, every, no, which
      NOUN 	noun 	year, home, costs, time, Africa
      NUM 	numeral 	twenty-four, fourth, 1991, 14:24
      PRT 	particle 	at, on, out, over per, that, up, with
      PRON 	pronoun 	he, their, her, its, my, I, us
      VERB 	verb 	is, say, told, given, playing, would
      . 	punctuation marks 	. , ; !
      X 	other 	ersatz, esprit, dunno, gr8, univeristy
    Source:
    - https://www.nltk.org/api/nltk.tokenize.html
    - https://www.nltk.org/api/nltk.tag.pos_tag.html; https://www.nltk.org/book/ch05.html
    """
    # Only check length for non punctuation
    if (pos != '.' and len(token) < 2) \
    or pos is not None and pos in TokenUtils.EXCLUDED_POS \
    or token in TokenUtils.ENGLISH_STOPWORDS \
    or re.search(TokenUtils.BETWEEN_PAR_PATTERN, token):
      return True
    else:
      return False
