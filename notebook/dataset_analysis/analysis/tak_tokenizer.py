from io import StringIO
from typing import List
import pandas as pd
import numpy as np
import itertools
import re
import nltk
# Following NLTK dependencies must be installed.
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('universal_tagset')
from collections import Counter
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer # recommended lemmatizer for plural forms
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag

from .token_utils import TokenUtils


class TAKTokenizer:

  CLEAN_SUFFIX = '(clean)'

  ENGLISH_STOPWORDS = set(stopwords.words('english'))
  BETWEEN_PAR_PATTERN = '[\(\[].*?[\)\]]'

  SENTENCE_SEPARATOR = '. '
  SENTENCE_SEPARATOR_NO_SPACE = '.'


  def __init__(self, scopus_dataset: str, columns:List[str]):
    """
    scopus_dataset: Dataset filepath (Excel format).
    columns: TAK column and optionnaly a cluster column.
      ['Title', 'Abstract', 'Author Keywords', 'Cluster' OR 'VOS cluster']
    """
    self.__scopus_dataset: str = scopus_dataset
    self.__df: pd.DataFrame = None
    self.__colums: List[str] = columns
    self.__titles_cleaned = []
    self.__abstracts_cleaned = []
    self.__auth_keywords_cleaned = []


  def prepare(self):
    self.__df: pd.DataFrame = pd.read_excel(self.__scopus_dataset, sheet_name=0)
    self.__df = self.__df[self.__colums]
    self.__df = self.__df.astype('str') # Force str type


  def process(self):
    """
    Clean and tokenize.
    """
    self._clean_title()
    self._clean_abstract()
    self._clean_author_keywords()
    self._create_tak_col()


  def filter(self, col_name:str, values):
    self.__df = self.__df[self.__df[col_name].isin(values)]


  def _clean_title(self):
    for title in self.__df['Title']:
      sentences = TokenUtils.tokenize(title)
      self.__titles_cleaned.append(sentences)


  def _clean_abstract(self):
    for abstract in self.__df['Abstract']:
      sentences = TokenUtils.tokenize(TAKTokenizer.sponsor_sentence_remover(abstract))
      self.__abstracts_cleaned.append(sentences)


  def _clean_author_keywords(self):
    """
    Author keywords are separated by '; '
    Perform a technical cleaning.
    A dot is used in join for tokenizer.
    """

    for auth_keywords in self.__df['Author Keywords']:
      if not auth_keywords:
        self.__auth_keywords_cleaned.append([])
        continue

      self.__auth_keywords_cleaned.append(TokenUtils.keywords_tokenize(auth_keywords))


  def _create_tak_col(self):
    """
    Create TAK column.
    """

    # Check size of TAK cleaned cols
    if len(self.__titles_cleaned) != len(self.__abstracts_cleaned) != len(self.__auth_keywords_cleaned):
      raise ValueError('TAK prepared columns have not the same length.')

    nb_rows = len(self.__titles_cleaned)

    tak_col = []
    for i in range(0, nb_rows):
      title = self.__titles_cleaned[i]
      abstract = self.__abstracts_cleaned[i]
      keywords = self.__auth_keywords_cleaned[i]

      tak_buffer = StringIO()
      if len(title) > 0:
        tak_buffer.write(TokenUtils.join(TokenUtils.flatten(title)))

      if len(abstract) > 0:
        tak_buffer.write(TokenUtils.join(TokenUtils.flatten(abstract)))

      if len(keywords) > 0:
        tak_buffer.write(TokenUtils.join(keywords))

      tak_col.append(tak_buffer.getvalue())

    self.__df['TAK (tokens)'] = tak_col


  def all_tak_tokens(self) -> List[str]:
    # Check size of TAK cleaned cols
    if len(self.__titles_cleaned) != len(self.__abstracts_cleaned) != len(self.__auth_keywords_cleaned):
      raise ValueError('TAK prepared columns have not the same length.')

    nb_rows = len(self.__titles_cleaned)

    all_tokens = []
    for i in range(0, nb_rows):
      title = self.__titles_cleaned[i]
      abstract = self.__abstracts_cleaned[i]
      keywords = self.__auth_keywords_cleaned[i]

      all_tokens.extend(TokenUtils.flatten(title))
      all_tokens.extend(TokenUtils.flatten(abstract))
      all_tokens.extend(keywords)

    return all_tokens


  def get_df(self):
      return self.__df


  @staticmethod
  def sponsor_sentence_remover(abstract:str) -> str:
    """
    Remove sponsor parts in abstracts.
    Possible values:
      © 2010 IEEE.
      © 2021 Owner/Author.
      © 2017 ACM.
      Copyright 2012 ACM.
      © 2020 Association for Computing Machinery.
      Copyright 2013 ACM.
      © 1992-2012 IEEE.
      © 2018 Copyright is held by the owner/author(s).
      © 2019 Copyright held by the owner/author(s). Publication rights licensed to ACM.
      © 2018 Copyright is held by the owner/author(s).
      © 2018 Association for Computing Machinery.
      Copyright © 2014 by the Association for Computing Machinery, Inc. (ACM).
      ©2010 ieee
    """

    pattern = re.compile(' ?(?i:copyright[ \t]*)?(?:\(c\)|&#(?:169|xa9;)|©)?([ \t]+)?(?:19|20)[0-9]{2}')
    m = pattern.search(abstract)
    if m is None:
      return abstract

    match_range = m.span()
    abstract = abstract[0:match_range[0]] # Cut str at first span index
    return abstract
