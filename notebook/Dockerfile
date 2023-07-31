# Based on: https://jupyter-docker-stacks.readthedocs.io/en/latest/using/recipes.html

# Start from a core stack version
FROM jupyter/datascience-notebook:2023-06-01
# Install from the requirements.txt file
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt
# Additional NLTK dependencies. Will run the command and install the requested files to //nltk_data/
RUN python -m nltk.downloader averaged_perceptron_tagger punkt stopwords universal_tagset
