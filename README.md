# BLV-research-analysis

This repo contains the data and code for our ASSETS2023 blind and low-vision (BLV) research litterature review paper entitled *[A Large-Scale Mixed-Methods Analysis of Blind and Low-vision Research in ACM and IEEE](https://doi.org/10.1145/3597638.3608412)* by [Yong-Joon Thoo](https://yjthoo.human-ist.ch/), [Maximiliano Jeanneret Medina](https://human-ist.unifr.ch/en/institute/team/maximiliano-jeanneret-medina.html), [Jon E. Froehlich](https://jonfroehlich.github.io/), [Nicolas Ruffieux](https://www.unifr.ch/directory/en/people/1722/4732d) and [Denis Lalanne](https://human-ist.unifr.ch/en/institute/team/denis-lalanne.html). 

Please cite our work as:

> Yong-Joon Thoo, Maximiliano Jeanneret Medina, Jon E. Froehlich, Nicolas Ruffieux, and Denis Lalanne. 2023. A Large-Scale Mixed-Methods Analysis of Blind and Low-vision Research in ACM and IEEE. In The 25th International ACM SIGACCESS Conference on Computers and Accessibility (ASSETS '23), October 22–25, 2023, New York, NY, USA. ACM, New York, NY, USA, 20 pages. DOI:https://doi.org/10.1145/3597638.3608412

Please navigate to the `notebook` subfolder for a description of the notebooks and folders. You can run our analysis notebooks using [Docker](https://www.docker.com/) with the steps below. 

## Running the notebooks with Docker

This is based on:
* [Jupyter Docker Stacks documentation](https://jupyter-docker-stacks.readthedocs.io/en/latest/)
* [Docker Stacks GitHub page](https://github.com/jupyter/docker-stacks)

**Note:** For the following steps, please use the terminal and navigate to the `notebook` subfolder. 

### Build a Docker Image with Dependencies

Run the following command to build a Docker image with the name `jupyter/my-datascience-notebook`:

```
docker build --rm -t jupyter/my-datascience-notebook .
```

### Run a Docker container

Run the following command:

```
docker run -it --rm -p 10000:8888 -v "${PWD}":/home/jovyan/work jupyter/my-datascience-notebook
```

Once running, enter http://localhost:10000/ in your browser and use the token displayed in the terminal. You can then access the notebooks in the `work` folder. 

**Note:** The port has been set to `10000` (`10000:8888`).  