import pandas as pd
from typing import Counter, List
import nltk
#nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder, QuadgramCollocationFinder
bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()
fourgram_measures = nltk.collocations.QuadgramAssocMeasures()
from nltk.util import ngrams
import re


class CollocationProcessor:
    """
    Calculate collocations.
    Source:
    - https://www.nltk.org/_modules/nltk/collocations.html
    """

    PUNCTUATION = "\"#$%&'()*+,./:;<=>?@[\]^_`{|}~"  # Inspired by string.punctuation: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

    IGNORED_WORDS = set(stopwords.words("english"))
    for keep_word in ["and", "with", "or"]:
        IGNORED_WORDS.remove(keep_word)


    def __init__(self, tokens: List[str], min_freq_count: int):
        self.__tokens: List[str] = tokens
        self.__min_freq_count: int = min_freq_count  # Recommended, at least mentioned by 1% on the entire dataset.
        self.__df: pd.DataFrame = pd.DataFrame(
            {
                "ngrams": pd.Series(dtype="int"),
                "potential mwe": pd.Series(dtype="str"),
                "score": pd.Series(dtype="float"),
            }
        )


    def process(self, limit: int = 0):
        self._process_ngram_collocation(ngrams=1, limit=limit, force_limit=False)
        self._process_ngram_collocation(ngrams=2, limit=limit, force_limit=False)
        self._process_ngram_collocation(ngrams=3, limit=limit, force_limit=False)
        self._process_ngram_collocation(ngrams=4, limit=limit, force_limit=False)


    def _process_ngram_collocation(self,
                                   ngrams,
                                   limit: int = 500,
                                   force_limit: bool = False):
        """
        Process collocations from 1 to 4 grams.
        method: can be '' or 'raw_freq'
        """

        if ngrams < 1 or ngrams > 4:
            raise ValueError(
                "Ngrams must in range 1-4, actual value: " + str(ngrams)
            )

        # Process collocations
        if ngrams == 1:
            method = "raw_freq"  # Force raw frequency, other methods do not exists
            # Additional token separation can be placed here
            unigrams = CollocationProcessor.unigram_counts(
                self.__tokens
            ).most_common()  # Return all elements, sort by frequency (desc)
            scored = []
            for value, count in unigrams:
                unigram = " ".join(
                    value
                )  # necessary because can be bigram or more by default
                if len(unigram) > 2 and count >= self.__min_freq_count:
                    scored.append((unigram, count))  # tuple needed

        elif ngrams > 1 or ngrams < 5:
            method = "likelihood_ratio"
            if ngrams == 2:
                finder = BigramCollocationFinder.from_words(self.__tokens)
            if ngrams == 3:
                finder = TrigramCollocationFinder.from_words(self.__tokens)
            if ngrams == 4:
                finder = QuadgramCollocationFinder.from_words(self.__tokens)

            # Filtering, does not affect LLR ratio
            finder.apply_freq_filter(
                self.__min_freq_count
            )  # to limit further processing
            finder.apply_word_filter(
                lambda w: len(w) < 2
            )  # Filter by default punctuation
            # or re.match(TokenUtils.SENTENCE_SEPARATOR_PUNCT, w
            # w.lower() in CollocationProcessor.IGNORED_WORDS

            if ngrams == 2:
                scored = finder.score_ngrams(bigram_measures.likelihood_ratio)
            elif ngrams == 3:
                scored = finder.score_ngrams(trigram_measures.likelihood_ratio)
            elif ngrams == 4:
                scored = finder.score_ngrams(fourgram_measures.likelihood_ratio)

            if limit > 0:
                # The limit is changed to not trunc the set at one frequency count
                # The rows must be sorted by score (desc)
                if not force_limit and method == "raw_freq":
                    new_limit = 0
                    for ngram, score in scored:
                        if score >= self.__min_freq_count:
                            new_limit += 1
                        else:
                            break

                    if new_limit > limit:
                        limit = new_limit

                scored = scored[:limit]  # Retain a certain number of rows

        col_prep = []
        for ngram, score in scored:
            potential_mwe = " ".join(ngram) if ngrams > 1 else ngram
            # print(potential_mwe, ngram, score)
            col_prep.append(
                {
                    "method": method,
                    "ngrams": ngrams,
                    "potential mwe": potential_mwe,
                    "score": score,
                }
            )

        #self.__df = self.__df.append(col_prep) # Deprecated
        self.__df = pd.concat([self.__df,
                               pd.DataFrame.from_records(col_prep)])

        # Count n-grams in n+grams
        # 'assistive' (unigram) is in 'assistive technology' (bigram)
        mwe_count_col = []
        mwes_in_higher_ngrams_col = []
        for ngrams, mwe in zip(self.__df["ngrams"], self.__df["potential mwe"]):
            selection_df = self.__df[
                (self.__df["ngrams"] > ngrams)
                & (self.__df["potential mwe"].str.contains(mwe))
            ]
            mwes_in_higher_ngrams = "; ".join(selection_df["potential mwe"])
            mwes_in_higher_ngrams_col.append(mwes_in_higher_ngrams)
            mwe_count_col.append(len(selection_df))
        self.__df["In higher ngrams"] = mwes_in_higher_ngrams_col
        self.__df["In higher ngrams (count)"] = mwe_count_col


    def count_ngrams_in(self, abstracts: pd.Series):
        """
        Count if mwe exists in abstracts
        """

        # Count terms in asbtract
        in_abstracts_col = []
        occurrences_col = []
        for ngrams, mwe in zip(self.__df["ngrams"], self.__df["potential mwe"]):

            in_abstracts = 0
            occurrences = 0
            for abstract in abstracts:
                # Easy find (binary)
                if mwe in abstract:
                    in_abstracts += 1

                # Patttern find (0 to n), nb occurrences
                founds = re.findall(mwe, abstract)
                if len(founds) > 0:
                    occurrences += len(founds)

            in_abstracts_col.append(in_abstracts)
            occurrences_col.append(occurrences)

        self.__df["In nb abstracts"] = in_abstracts_col
        self.__df["Nb occurrences"] = occurrences_col


    def get_df(self):
        return self.__df


    @staticmethod
    def unigram_counts(words: List[str]) -> Counter:
        """
        https://github.com/yyht/BERT/blob/master/t2t_bert/nlm_noisy_generator/utils.py
        https://docs.python.org/3/library/collections.html#collections.Counter
        """
        unigrams = ngrams(words, 1)
        fdist = nltk.FreqDist(unigrams)
        d = Counter()
        for k, v in fdist.items():
            d[k] = v
        return d
