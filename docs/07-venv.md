# Python virtual environment

## Creating python virtual environment for development

- You can use either `conda` or `venv` to create virtual environment.
- I am using `conda` for this project.

## Prerequisites

- conda installed from [here](https://docs.conda.io/en/latest/miniconda.html)

## Create a conda environment

- cd navigate to the root of the project

```bash
cd path/to/fastapi-poc
```

- create a conda environment

```bash
conda env create -f conda-env.yml
```

- activate the environment

```bash
conda activate process-api
```

- update the conda environment

```bash
conda env update -f conda-env.yml
```

- update conda via requirements.txt

```bash
conda activate process-api
pip install -r requirements.txt
```
