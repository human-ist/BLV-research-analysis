import pandas as pd
import re
from typing import Dict, List, Tuple


class KeywordSearchAnalyzer:
  """
  Research terms analyzer.
  Analyze the keywords in title, abstract and author keywords (TAK)

  Based on:
    - Writing a Tokenizer: https://docs.python.org/3/library/re.html#writing-a-tokenizer

    - https://stackoverflow.com/questions/39291499/how-to-concatenate-multiple-column-values-into-a-single-column-in-pandas-datafra
    - https://toltman.medium.com/matching-multiple-regex-patterns-in-pandas-121d6127dd47
    - https://towardsdatascience.com/check-for-a-substring-in-a-pandas-dataframe-column-4b949f64852
    - https://stackoverflow.com/questions/64750419/how-to-use-two-regex-capture-groups-to-make-two-pandas-columns

    - https://stackoverflow.com/questions/4697882/how-can-i-find-all-matches-to-a-regular-expression-in-python
    - https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
  """

  # To search in TAK, only TA, only T, A or K
  SEARCH_COLS = ['TAK', 'TA', 'T', 'A', 'K']

  def __init__(self, 
               scopus_dataset: str = None, 
               df: pd.DataFrame = None, 
               keywords_search_spec: List[Tuple[str, str]] = None, 
               search_in_cols: str = 'TAK'):
    """
    Load a dataset according to its filepath.
    If no filepath, the pandas dataset must be passed as param.
    """
    self.__df: pd.DataFrame = None
    if scopus_dataset is not None:
      self.__scopus_dataset: str = scopus_dataset
      self.__df: pd.DataFrame = pd.read_excel(self.__scopus_dataset, sheet_name=0)

    elif df is not None:
      self.__df: pd.DataFrame = df

    self.__keywords_search_spec:list[tuple[str, str]] = keywords_search_spec
    self.__keyword_occurrence_df: pd.DataFrame = None
    self.__keyword_crosstab_df: pd.DataFrame = None

    self.__pattern:str = None

    # Temporal
    self.__keyword_temporal_crosstab_df: pd.DataFrame = None

    if search_in_cols not in KeywordSearchAnalyzer.SEARCH_COLS:
      raise ValueError(search_in_cols + ' must be in [' + ', '.join(KeywordSearchAnalyzer.SEARCH_COLS) + '].')
    self.__search_in_cols: str = search_in_cols
  

  def prepare(self):
    """
    Pattern preparation: https://docs.python.org/3/library/re.html#writing-a-tokenizer
    """
    
    cols = [] # ['Title', 'Abstract', 'Author Keywords']

    if 'T' in self.__search_in_cols:
      cols.append('Title')
    if 'A' in self.__search_in_cols:
      cols.append('Abstract')
    if 'K' in self.__search_in_cols:
      cols.append('Author Keywords')
    
    if len(cols) < 1:
      raise ValueError('At least one column must be defined for search: ' + self.__search_in_cols)

    separator = '. '
    self.__df[self.__search_in_cols] = self.__df[cols].apply(lambda row: separator.join(row.values.astype(str)), axis=1)
    # TODO clean with POS if necessary ---------------------
    self.__df[self.__search_in_cols] = self.__df[self.__search_in_cols].apply(str.lower)
    # Pattern with named groups
    self.__pattern: str = '|'.join('(?P<%s>%s)' % pair for pair in self.__keywords_search_spec)
  

  def process(self):
    
    keyword_occurrences_arr = []

    for doi, year, tak in zip(self.__df['DOI'], self.__df['Year'], self.__df[self.__search_in_cols]):
      # Find match and group
      for match_obj in re.finditer(self.__pattern, tak):
        keyword_searched = match_obj.lastgroup
        value = match_obj.group()
        #print(keyword_searched, value)
        keyword_occurrences_arr.append({"DOI": doi,
                                        "Year": year,
                                        "keyword": keyword_searched,
                                        "term": value })
    
    self.__keyword_occurrence_df = pd.DataFrame(keyword_occurrences_arr)

    # Create a crosstab
    self._process_crosstab()
  

  def _process_crosstab(self) -> pd.DataFrame:
    """
    Process a matrix DOI x keyword in TAK.
    """
    self.__keyword_crosstab_df = pd.crosstab(index=[self.__keyword_occurrence_df['DOI']],
                                             columns=[self.__keyword_occurrence_df['keyword']],
                                             dropna=False,
                                             margins=True, # Adding margins (Subtotals on the ends),
                                             margins_name="Totals").reset_index().fillna(0)
    self.__keyword_crosstab_df = self.__keyword_crosstab_df.iloc[:-1] # Remove column total (last row)
  

  def process_categories_groups(self) -> pd.DataFrame:
    """
    Binary counting (do not count occurrences) of the presence of query terms in groups.
    The number of distinct sorted set is the number of population combinations

    [
      [PVI, PLV, B]
      [0, 1, 1]
    ]
    ->
    BxPLV (str) (respect alphabetical order)
    """
    categories_groups_arr = [] # One or more categories

    # Get columns excluding totals
    df = self.__keyword_crosstab_df.iloc[:, 1:-1]
    columns = df.columns

    for index, row in df.iterrows(): # Loop as a k, v / not as a index basis
      categories_group = set()
      for col in columns:
        term_occurrences = row[col]
        if term_occurrences > 0:
          categories_group.add(col)
      
      # sort set asc and join
      sorted(categories_group)
      categories_group_str = 'x'.join(categories_group)
      categories_groups_arr.append(categories_group_str)
    
    categories_groups_df = pd.DataFrame(categories_groups_arr, columns=['categories_group'])

    # Group by
    grouped = categories_groups_df.groupby("categories_group")["categories_group"].count().sort_values(ascending=False)

    # Create memberships with filter
    all_groups_arr = []
    data_arr = []
    for group, value in grouped.items():
      group_arr = group.split('x')
      all_groups_arr.append(group_arr)
      data_arr.append(value)

    return categories_groups_df, all_groups_arr, data_arr
  

  # Temporal Crosstab Region

  def __count_pub_per_year(self) -> pd.DataFrame:
    """
    Count the number of papers per year.
    Count must be performed on 'self.__df' to have all rows and not only those with an identified term.
    """
    return self.__df['Year'].groupby(self.__df['Year']).agg('count')


  def process_temporal(self):
    self._process_temporal_crosstab()
  

  def _process_temporal_crosstab(self) -> pd.DataFrame:
    """
    Process a matrix Year x keyword in TAK.
    """
    # Get uniques to not count keywords twice
    #print(len(self.__keyword_occurrence_df))
    self.__keyword_occurrence_df = self.__keyword_occurrence_df.groupby(['DOI', 'Year', 'keyword']).size().reset_index()
    #print(len(self.__keyword_occurrence_df))

    # Crosstab
    self.__keyword_temporal_crosstab_df = pd.crosstab(index=[self.__keyword_occurrence_df['keyword']],
                                             columns=[self.__keyword_occurrence_df['Year']],
                                             dropna=False,
                                             margins=False) \
                                             .reset_index().fillna(0)
    self.__keyword_temporal_crosstab_df = self.__keyword_temporal_crosstab_df.set_index('keyword')

    # Normalize
    total_pubs_per_year = self.__count_pub_per_year().values
    #print(total_pubs_per_year)
    self.__keyword_temporal_crosstab_df = self.__keyword_temporal_crosstab_df.div(total_pubs_per_year, axis=1)
  
  
  def get_docs_without_keyword_mention(self) -> pd.DataFrame:
    if self.__keyword_crosstab_df is None or \
      self.__df is None:
      return pd.DataFrame() # Empty

    valid_DOIs = self.__keyword_crosstab_df['DOI'].values.tolist()
    no_mention_keyword_df = self.__df[~self.__df['DOI'].isin(valid_DOIs)]
    return no_mention_keyword_df[['Authors', self.__search_in_cols, 'DOI']]
  

  '''def output(self, filepath):
    self.__df_output.to_excel(filepath, index=False)'''

  
  def get_pattern(self) -> str:
    return self.__pattern
  
  
  def get_keyword_occurrence_df(self) -> pd.DataFrame:
    return self.__keyword_occurrence_df
  

  def set_keyword_occurrence_df(self, keyword_occurrence_df):
    self.__keyword_occurrence_df = keyword_occurrence_df
  

  def get_keyword_crosstab_df(self) -> pd.DataFrame:
    return self.__keyword_crosstab_df
  

  def set_keyword_crosstab_df(self, keyword_crosstab_df):
    self.__keyword_crosstab_df = keyword_crosstab_df


  def get_keyword_temporal_crosstab_df(self) -> pd.DataFrame:
    return self.__keyword_temporal_crosstab_df


  def summary(self):
    if self.get_pattern():
      print('Patterns: ' + self.get_pattern())
    
    #print(analyzer.get_keyword_occurrence_df())
    
    if self.get_keyword_crosstab_df() is not None and \
      len(self.get_keyword_crosstab_df()) > 0:
      print(self.get_keyword_crosstab_df())
    
    if self.get_docs_without_keyword_mention() is not None and \
      len(self.get_docs_without_keyword_mention()) > 0:
      docs_without_keyword_mention = self.get_docs_without_keyword_mention()
      print(len(docs_without_keyword_mention.index))
      print(self.get_docs_without_keyword_mention())
