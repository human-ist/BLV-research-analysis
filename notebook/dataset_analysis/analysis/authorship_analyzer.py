import pandas as pd
import numpy as np


class AuthorshipAnalyzer:
    """

    """

    def __init__(self, df: pd.DataFrame):
        """
        Columns: 'Author(s) ID', 'DOI', 'Sponsor (clean)'
        """
        self.__df: pd.DataFrame = df
        self.__prep_df: pd.DataFrame = None
    

    def prepare(self):
        """
        Initially, one author(s) can contains multiple authors.
        """
        # Prepare the dataframe with minimal columns and one author per row.
        filt_df = self.__df[['Author(s) ID', 'DOI', 'Sponsor (clean)']]

        prep_df = pd.DataFrame(filt_df['Author(s) ID'].str.split(';').tolist(),
                               index=filt_df['DOI']).stack()
        prep_df = prep_df.reset_index([0, 'DOI'])
        prep_df.columns = ['DOI', 'Author(s) ID']
        prep_df = prep_df[prep_df['Author(s) ID'] != ''] # Because separators are placed at the end of the string

        # Get sponsor column
        sponsors = []
        for doi in prep_df['DOI']:
            sponsor =  filt_df[filt_df['DOI'] == doi]['Sponsor (clean)'].iloc[0]
            sponsors.append(sponsor)
        prep_df['Sponsor (clean)'] = sponsors
        self.__prep_df = prep_df


    def authors_per_paper_summary(self):
        count_authors_per_paper = self.__prep_df.groupby(['DOI']).size().reset_index(name='counts')
        count_authors_per_paper_summary_df = count_authors_per_paper.describe().loc[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        return count_authors_per_paper_summary_df


    def papers_per_author_summary(self):
        count_contrib_per_author = self.__prep_df.groupby(['Author(s) ID']).size().reset_index(name='counts').sort_values("counts", ascending=False)
        count_contrib_per_author_summary_df = count_contrib_per_author.describe().loc[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        return count_contrib_per_author_summary_df
    
    def authors_contrib_per_sponsor(self):
        """
        Create a pivot table with one author per row and the number of sponsor contribution per column.
        Only keep row total.
        """
        authors_contrib_per_sponsor_df = self.__prep_df.pivot_table(values='DOI',
                                                                    index='Author(s) ID',
                                                                    columns='Sponsor (clean)',
                                                                    aggfunc='count',
                                                                    margins=True,
                                                                    fill_value=0).reset_index()
        # Remove end row (column total)
        authors_contrib_per_sponsor_df.drop(authors_contrib_per_sponsor_df.tail(1).index,
                                            inplace=True)
        return authors_contrib_per_sponsor_df
    

    def authors_contrib_multiple_sponsors(self, complete:bool = False):
        authors_contrib_per_sponsor_df = self.authors_contrib_per_sponsor()

        # Flag authors who contributer to multiple sponsors
        flag_multi_list = []
        for acm, both, ieee, all in zip(authors_contrib_per_sponsor_df['ACM'],
                                        authors_contrib_per_sponsor_df['ACM/IEEE'],
                                        authors_contrib_per_sponsor_df['IEEE'],
                                        authors_contrib_per_sponsor_df['All']):
            if all <= 1:
                flag_multi_list.append(0)

            elif (acm >= 1 and both >=1) or \
                (acm >= 1 and ieee >=1) or \
                    (both >= 1 and ieee >=1):
                flag_multi_list.append(1)

            else:
                flag_multi_list.append(0)
        authors_contrib_per_sponsor_df['flag'] = flag_multi_list
        #print(authors_contrib_per_sponsor_df)

        authors_contrib_mult_sponsors_df = authors_contrib_per_sponsor_df[authors_contrib_per_sponsor_df['flag'] == 1]
        authors_contrib_mult_sponsors_df = authors_contrib_mult_sponsors_df.drop('flag', axis=1)
        authors_contrib_mult_sponsors_df = authors_contrib_mult_sponsors_df.set_index('Author(s) ID')

        if not complete:
            return authors_contrib_mult_sponsors_df
        
        # Get DOIs of published units per author
        all_dois = []
        all_sponsors = []
        for auth_id in authors_contrib_mult_sponsors_df['Author(s) ID']:
            dois =  self.__prep_df[self.__prep_df['Author(s) ID'] == auth_id]['DOI'].to_list()
            all_dois.append('; '.join(dois))

            sponsors =  self.__prep_df[self.__prep_df['Author(s) ID'] == auth_id]['Sponsor (clean)'].to_list()
            all_sponsors.append('; '.join(sponsors))

        authors_contrib_mult_sponsors_df['DOIs'] = all_dois
        authors_contrib_mult_sponsors_df['Sponsors'] = all_sponsors
        authors_contrib_mult_sponsors_df = authors_contrib_mult_sponsors_df.sort_values(['All', 'ACM', 'IEEE'], ascending=[0, 0, 0])
        return authors_contrib_mult_sponsors_df


    def summary(self):
        n_papers = self.__prep_df['DOI'].nunique()
        n_authors = self.__prep_df['Author(s) ID'].nunique()
        summary_dict = {
            'Papers': n_papers,
            'Authors': n_authors
        }
        return summary_dict
