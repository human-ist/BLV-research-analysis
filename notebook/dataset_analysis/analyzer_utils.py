import os
import pandas as pd
from matplotlib import pyplot as plt
from upsetplot import plot, from_memberships
from typing import Dict, List
from dataset_analysis.analysis.keyword_search_analyser import KeywordSearchAnalyzer
from dataset_analysis.analysis.temporal_plot_data import TemporalPlotData
from .viz_utils import multiple_line_plot
from dataset_analysis.analysis.tak_tokenizer import TAKTokenizer
from dataset_analysis.analysis.collocation_processor import CollocationProcessor
from .file_utils import rename_with_clust

"""
Service methods to run analyzer.
Act as a facade to analysis classes.
"""

# region TAK analysis

def __count_nb_group_multiple_terms(all_groups_arr, data_arr):
  multiple_group_arr = []
  for i in range(len(all_groups_arr)):
    if len(all_groups_arr[i]) > 1:
      multiple_group_arr.append({"Group": 'x'.join(all_groups_arr[i]),
                                 "count": data_arr[i]})

  multiple_group_arr_df = pd.DataFrame(multiple_group_arr)
  print(multiple_group_arr_df)
  print("Sum:")
  print(multiple_group_arr_df['count'].sum())


def _upset_plot(categories_groups_df, 
                all_groups_arr,
                data_arr,
                rename_dict,
                figname_no_ext:str,
                fig_folder_path:str):
  """
  Plot sets and save figure in PNG.
  """
  if rename_dict is not None:
      renamed_all_groups_arr = []
      for elem in all_groups_arr:
        renamed_all_groups_arr.append([rename_dict.get(n, n) for n in elem])
      all_groups_arr = renamed_all_groups_arr

  print(data_arr)
  print(all_groups_arr)
  print(categories_groups_df)
  __count_nb_group_multiple_terms(all_groups_arr, data_arr)

  upset_data = from_memberships(all_groups_arr, data=data_arr)
  plot(
    upset_data, show_counts=True, min_subset_size=5, sort_by='cardinality',
    element_size=25, intersection_plot_elements=10, totals_plot_elements=10
  )
  figpath = os.path.join(fig_folder_path, figname_no_ext)
  plt.savefig(f'{figpath}.png', format='png', dpi=400, bbox_inches = 'tight')
  # plt.savefig(f'{figname}.eps', format='eps', bbox_inches = 'tight')
  plt.show()


def regexp_counter_analysis(df:pd.DataFrame,
                            keywords_search_spec:Dict[str, str],
                            search_in:str,
                            out_filepath:str,
                            excluded_out_filepath:str,
                            figname:str,
                            fig_folder_path:str,
                            rename_dict: dict = None):
    """
    Analyze a dataset with terms.
    Start with regexp.

    :param df: Dataset.
    :param keywords_search_spec: Dictionnary of regular expressions.
      Important to respect a matching order with a OR condition.
      Because order matters, englobing expressions must be placed first.
    :param search_in: TAK.
    :param out_filepath: Output filepath of the crosstab 'document X terms'.
    :param excluded_out_filepath: Output filepath of the document that will contains documents where no terms have been found.
    :param figname: Name of the figure.
    :param rename_dict: Dictionnary to rename terms of regexp expressions that are strict.
    :return: None
    """
    # Preparation and processing
    analyzer = KeywordSearchAnalyzer(scopus_dataset=None,
                                     df=df,
                                     keywords_search_spec=keywords_search_spec,
                                     search_in_cols=search_in)
    analyzer.prepare()
    analyzer.process()

    analyzer.get_keyword_occurrence_df().to_excel(out_filepath.replace(".xlsx", "_complete.xlsx"), index=False)
    analyzer.get_keyword_crosstab_df().to_excel(out_filepath, index=False)
    analyzer.get_docs_without_keyword_mention().to_excel(excluded_out_filepath, index=False)

    # To cluster data, see also https://stackoverflow.com/questions/57457651/upsetr-manually-order-set-intersections-to-align-multiple-upset-plots
    categories_groups_df, all_groups_arr, data_arr = analyzer.process_categories_groups()
    analyzer.summary()

    _upset_plot(categories_groups_df, 
                all_groups_arr,
                data_arr,
                rename_dict,
                figname,
                fig_folder_path)


def crosstab_analysis(keyword_crosstab_df:pd.DataFrame,
                      figname:str,
                      fig_folder_path:str,
                      rename_dict: dict = None):
    """
    Analyze a dataset with terms.

    :param keyword_crosstab_df: Crosstab 'document X terms'.
    :param figname: Name of the figure.
    :param rename_dict: Dictionnary to rename terms of regexp expressions that are strict.
    :return: None
    """
    DUMMY_TAK = 'TAK'
    # Preparation and processing
    analyzer = KeywordSearchAnalyzer(scopus_dataset=None,
                                     df=None,
                                     keywords_search_spec=None,
                                     search_in_cols=DUMMY_TAK)
    analyzer.set_keyword_crosstab_df(keyword_crosstab_df)

    # To cluster data, see also https://stackoverflow.com/questions/57457651/upsetr-manually-order-set-intersections-to-align-multiple-upset-plots
    categories_groups_df, all_groups_arr, data_arr = analyzer.process_categories_groups()
    analyzer.summary()

    _upset_plot(categories_groups_df, 
                all_groups_arr,
                data_arr,
                rename_dict,
                figname,
                fig_folder_path)


def __temporal_plot(temporal_crosstab_df: pd.DataFrame,
                    rename_dict: Dict,
                    fig_folder_path: str,
                    figname_no_ext:str,
                    plot_width:int=400,
                    plot_height:int=700):
    # Multiplot
    all_temporal_plot_data = []
    for index, row in temporal_crosstab_df.iterrows():
      #print(row.index.values.tolist())
      #print(row.values.tolist())
      title = index.replace('_', ' ')
      if rename_dict is not None:
        title = rename_dict.get(index)

      x = row.index.values.tolist()
      y = row.values.tolist()
      temporal_plot_data = TemporalPlotData(title=title, x=x, y=y)
      all_temporal_plot_data.append(temporal_plot_data)

    figpath = os.path.join(fig_folder_path, figname_no_ext)

    multiple_line_plot(multiplot_title="",
                       temp_plots=all_temporal_plot_data,
                       figname=figpath,
                       width=plot_width,
                       height=plot_height)
   

def temporal_analyzer(df:pd.DataFrame,
                      keywords_search_spec:Dict[str, str],
                      search_in:str,
                      out_filepath:str,
                      excluded_out_filepath:str,
                      fig_folder_path:str,
                      figname_no_ext:str,
                      rename_dict: dict = None,
                      plot_width:int=400,
                      plot_height:int=700):
    # Preparation and processing
    analyzer = KeywordSearchAnalyzer(scopus_dataset=None,
                                     df=df,
                                     keywords_search_spec=keywords_search_spec,
                                     search_in_cols=search_in)
    analyzer.prepare()
    analyzer.process()

    analyzer.get_keyword_occurrence_df().to_excel(out_filepath.replace(".xlsx", "_complete.xlsx"), index=False) 
    analyzer.get_keyword_crosstab_df().to_excel(out_filepath, index=False)
    analyzer.get_docs_without_keyword_mention().to_excel(excluded_out_filepath, index=False)
    analyzer.summary()

    analyzer.process_temporal()
    print(analyzer.get_keyword_temporal_crosstab_df())

    __temporal_plot(temporal_crosstab_df=analyzer.get_keyword_temporal_crosstab_df(),
                    rename_dict=rename_dict,
                    fig_folder_path=fig_folder_path,
                    figname_no_ext=figname_no_ext,
                    plot_width=plot_width,
                    plot_height=plot_height)


def temporal_analyzer_from_crosstab(doi_year_df:pd.DataFrame,
                                    keyword_occurrence_df:pd.DataFrame,
                                    fig_folder_path:str,
                                    figname_no_ext:str,
                                    rename_dict: dict = None,
                                    plot_width:int=400,
                                    plot_height:int=700):
    # Preparation and processing
    analyzer = KeywordSearchAnalyzer(scopus_dataset=None,
                                     df=doi_year_df,
                                     keywords_search_spec=None,
                                     search_in_cols='TAK')
    analyzer.set_keyword_occurrence_df(keyword_occurrence_df)
    analyzer.summary()

    analyzer.process_temporal()
    print(analyzer.get_keyword_temporal_crosstab_df())

    __temporal_plot(temporal_crosstab_df=analyzer.get_keyword_temporal_crosstab_df(),
                    rename_dict=rename_dict,
                    fig_folder_path=fig_folder_path,
                    figname_no_ext=figname_no_ext,
                    plot_width=plot_width,
                    plot_height=plot_height)
    

def count_terms(dataset_filepath:str,
                tak_columns:List[str] = ['Title', 'Abstract', 'Author Keywords'],
                cluster_col:str = None,
                cluster_values:List[str] = ['1'],
                out_folder_path:str = None):
  """
  Count the terms in the TAK columns.
  If cluster_col is set, create multiple analysis. One analysis per cluster.
  tak_columns: ['Title', 'Abstract', 'Author Keywords']
  cluster_col:  'VOS cluster' or 'Cluster'
  """
  # Prepare columns
  if cluster_col is not None:
    tak_columns.append(cluster_col)
  print(tak_columns)

  for cluster in cluster_values:   
    # Prepare
    tokenizer = TAKTokenizer(scopus_dataset=dataset_filepath, columns=tak_columns)
    tokenizer.prepare()
    tokenizer.filter(col_name=cluster_col, values=[cluster])
    print(cluster, len(tokenizer.get_df()))
    tokenizer.process()
    tak_tokens = tokenizer.all_tak_tokens()
    #dataset_cluster_filepath = rename_with_clust(filepath=dataset_filepath, cluster=str(cluster))
    #Only if necessary: tokenizer.get_df().to_excel(dataset_cluster_filepath, index=False)

    # Process
    # Keep >= top 2% of terms occurrence
    min_freq_count = len(tokenizer.get_df()) * 0.02
    coloc_processor = CollocationProcessor(tokens=tak_tokens, min_freq_count=min_freq_count)
    coloc_processor.process(limit=100)

    tak_tokens = tokenizer.get_df()['TAK (tokens)']
    coloc_processor.count_ngrams_in(tak_tokens)
    collocations_cluster_filepath = os.path.join(out_folder_path, "collocations_cluster" + cluster[0] + ".xlsx")
    coloc_processor.get_df().to_excel(collocations_cluster_filepath, index=False)


# endregion


# region Pandas Utils

def count_with_percentage(df:pd.DataFrame, col_name:str):
  df_grouped = df.groupby([col_name]).size().reset_index(name='Nb').sort_values(by='Nb', ascending=False)
  df_grouped["Perc."] = round(df_grouped["Nb"]/df_grouped["Nb"].sum()*100, 1)
  return df_grouped


# endregion