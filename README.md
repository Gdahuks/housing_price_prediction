[![Code style: black](https://img.shields.io/badge/Code_style-black-black
)](https://github.com/psf/black)
[![linter](https://img.shields.io/badge/1st__Linter-PyLint-9acd32
)](https://github.com/pylint-dev/pylint)
[![Flake8](https://img.shields.io/badge/2nd__Linter-Flake8-ADD8E6
)](https://github.com/PyCQA/flake8)
[![Checked with mypy](https://img.shields.io/badge/Types_check-MyPy-blue
)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/Security-bandit-yellow)](https://github.com/PyCQA/bandit)


# House pricing prediction ML pipeline

This project was made as a final exercise for a data-oriented programming course at the Uniwersity of Gadańsk.

It scrapes data from 2 big real state listing portals, saves it into Azure Blob Storage in a JSON format and lets you train and use different ML models based on fetched data. We also provided an API layer to let end-users easly interact with a system. Belowe you can see diagram representing the system design.

![system diagram](https://i.ibb.co/Qd0YfHc/Unknown.jpg)

## Tech stack

- FastAPI
- Azure Blob Storage
- dvc (with Azure Blob Storage)
- BeautifulSoup4

## Deploy