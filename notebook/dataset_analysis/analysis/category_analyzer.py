import pandas as pd
import numpy as np


class CategoryAnalyzer:
  """
  
  """


  def __init__(self, filtered_df: pd.DataFrame):
      self.__filtered_df: pd.DataFrame = filtered_df


  def count(self) -> pd.DataFrame:
    """
    Count per category
    """
    filtered_df = self.__filtered_df.copy()

    print(filtered_df.columns)
    # TODO be sure to keep unique categories to not count twice

    nb_papers = len(filtered_df['DOI'].unique())
    print(nb_papers)
    #assert len(DOIs) == len(df_ST_art.DOI.unique())

    nb_codes = len(filtered_df)
    print(nb_codes)

    # Important. Get unique DOI-Code to have unique rows
    filtered_df = filtered_df.groupby(['DOI', 'Code']).first().reset_index()

    filtered_df_groups = filtered_df.pivot_table(values='DOI',
                                                  index=['Code'],
                                                  aggfunc='count').reset_index() \
                                                  .sort_values(['DOI', 'Code'], ascending=[0, 1])
    filtered_df_groups.rename(columns={"DOI": "Nb"}, inplace = True)
    filtered_df_groups["Perc."] = round(filtered_df_groups["Nb"]/nb_papers*100, 1)
    return filtered_df_groups


  def count_matrix(self):
    filtered_df = self.__filtered_df.copy()

    # Prepare
    # Important. Get unique DOI-Code to have unique rows
    filtered_df = filtered_df.groupby(['DOI', 'Code']).first().reset_index()

    unique_codes = filtered_df['Code'].unique()
    #print(unique_codes)

    filtered_df_selection = filtered_df[filtered_df['Code'].isin(unique_codes)]
    filtered_df_selection = filtered_df_selection[['DOI', 'Code']]
    #print(filtered_df_selection)
    #print(len(filtered_df_selection))

    filtered_df_matrix = pd.crosstab(index=filtered_df_selection['DOI'], columns=filtered_df_selection['Code'], margins=True)
    filtered_df_matrix =filtered_df_matrix[:-1] # remove last row (column total)

    return filtered_df_matrix


  def count_co_occurrences(self):
    filtered_df_matrix = self.count_matrix()
    filtered_df_matrix = filtered_df_matrix[filtered_df_matrix.columns[:-1]] # Remove last column (total column)
    print(filtered_df_matrix.columns)

    nb_papers = len(filtered_df_matrix)

    doi_coding_arr = []
    for doi, row in filtered_df_matrix.iterrows():
      coding_combination = []
      for k, v in row.items():
        if v > 0:
          #print(doi, k, v)
          coding_combination.append(k)

      # One combination per row
      doi_coding_arr.append({"DOI": doi,
                             "Coding": "x".join(coding_combination)})

    doi_coding_df = pd.DataFrame(doi_coding_arr)

    # Count
    doi_coding_df_groups = doi_coding_df.pivot_table(values='DOI',
                                                  index=['Coding'],
                                                  aggfunc='count').reset_index() \
                                                  .sort_values(['DOI', 'Coding'], ascending=[0, 1])
    doi_coding_df_groups.rename(columns={"DOI": "Nb"}, inplace = True)
    doi_coding_df_groups["Perc."] = round(doi_coding_df_groups["Nb"]/nb_papers*100, 1)
    return doi_coding_df_groups


  def count_to_latex(self):
    return self.__filtered_df_groups.to_latex(index=False,
                                              formatters={"name": str.upper},
                                              float_format="{:.1f}".format)
