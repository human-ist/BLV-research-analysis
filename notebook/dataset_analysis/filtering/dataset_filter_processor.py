import pandas as pd
from typing import List
from .pred_filter import PredefinedFilter


class DatasetFilterProcessor:
  """
  Filter a dataset:
    1. Automatically by identifying empty values
    2. Manually by parametrized filters.
      A column must be defined as filter: e.g., 'Filtered (manual)'
  """

  SCOPUS_ABSTRACT_NA_FLAG:str = '[No abstract available]'
  

  def __init__(self, scopus_dataset: str, predefined_filters:List[PredefinedFilter]):
    self.__scopus_dataset: str = scopus_dataset
    self.__df: pd.DataFrame = None
    self.__na_abstract_doi: List[str] = None
    self.__na_refs_doi: List[str] = None
    self.__na_doctype_doi: List[str] = None
    self.__predefined_filters: List[PredefinedFilter] = predefined_filters
  

  def process(self):
    # Load dataset
    self.__df: pd.DataFrame = pd.read_excel(self.__scopus_dataset, sheet_name=0)
    self.__load_summary = {"operation": "Load dataset",
                           "type": "N/A",
                           "nb rows": len(self.__df.index)}

    # Automatic filtering: Abstract and References
    self.__df.loc[self.__df["Abstract"] == DatasetFilterProcessor.SCOPUS_ABSTRACT_NA_FLAG, "Abstract"] = pd.NA # Replace Scopus flag by NA
    self.__na_abstract_doi = self.__df[self.__df['Abstract'].isna()]['DOI'].tolist()
    self.__na_refs_doi = self.__df[self.__df['References'].isna()]['DOI'].tolist()
    self.__na_doctype_doi = self.__df[self.__df['Document Type'].isna()]['DOI'].tolist()
    # Filter main dataframe
    self.__df = self.__df[self.__df[['Abstract', 'References', 'Document Type']].notnull().all(1)]

    # Predefined filtering
    for filter in self.__predefined_filters:
      predefined_filter_df = self.__df.loc[self.__df[filter.get_column_name()] == filter.get_flag()]
      filter.set_removed_dois(predefined_filter_df['DOI'].tolist())
      self.__df.drop(predefined_filter_df.index, inplace=True)
  

  def get_df(self) -> pd.DataFrame:
    return self.__df
  

  def get_all_removed_doi(self) -> List[str]: # TODO dataframe with reason and DOI
    all_doi_arr = [self.__na_abstract_doi, self.__na_refs_doi, self.__na_doctype_doi]
    for predefined_filter in self.__predefined_filters:
      all_doi_arr.append(predefined_filter.get_removed_dois())

    all_removed_doi:List[str] = []
    for doi_arr in all_doi_arr:
      for doi in doi_arr:
        all_removed_doi.append(doi)
    
    return all_removed_doi


  def summary(self) -> pd.DataFrame:
    summary_arr = []
    summary_arr.append(self.__load_summary)
    summary_arr.append({"operation": "Remove N/A abstract",
                        "type": "automatic",
                        "nb rows": len(self.__na_abstract_doi)})
    summary_arr.append({"operation": "Remove N/A references",
                        "type": "automatic",
                        "nb rows": len(self.__na_refs_doi)})
    summary_arr.append({"operation": "Remove N/A document type",
                        "type": "automatic",
                        "nb rows": len(self.__na_doctype_doi)})
    # Manual filtering
    for filter in self.__predefined_filters:
      summary_arr.append({"operation": filter.get_operation(),
                          "type": filter.get_type(),
                          "nb rows": filter.get_nb_removed_dois()})
    
    summary_arr.append({"operation": "Export dataset",
                        "type": "N/A",
                        "nb rows": len(self.__df.index)})

    return pd.DataFrame(summary_arr)
  

  def filter_initial_set(self, cleaned_dataset_path:str, output_path:str):
    """
    Filter the initial set with the DOI to remove
    """
    df = pd.read_csv(cleaned_dataset_path)
    # Filter rows and export to df
    df = df[~df['DOI'].isin(self.get_all_removed_doi())]
    df.to_csv(output_path, index=False)
