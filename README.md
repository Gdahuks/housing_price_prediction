[![Code style: black](https://img.shields.io/badge/Code_style-black-black
)](https://github.com/psf/black)
[![linter](https://img.shields.io/badge/1st__Linter-PyLint-9acd32
)](https://github.com/pylint-dev/pylint)
[![Flake8](https://img.shields.io/badge/2nd__Linter-Flake8-ADD8E6
)](https://github.com/PyCQA/flake8)
[![Checked with mypy](https://img.shields.io/badge/Types_check-MyPy-blue
)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/Security-bandit-yellow)](https://github.com/PyCQA/bandit)
[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]



# House pricing prediction ML pipeline


This project was made as a final exercise for a data-oriented programming course at the University of Gdańsk.

It scrapes data from 2 big real state listing portals, saves it into Azure Blob Storage in a JSON format and lets you train and use different ML models based on fetched data. We also provided an API layer to let end-users easly interact with a system. Below you can see diagram representing the system design.

## System design

The architecture of the system is depicted in the diagram below:

![system diagram](https://i.ibb.co/Qd0YfHc/Unknown.jpg)

### Note

This project is designed to showcase our Python skills. We prioritize model clarity over complexity, and while the unit test coverage is minimal, provided examples demonstrate our understanding of effective testing. The API design is intentionally streamlined for clarity and ease of understanding. Similarly, the data scraping component is kept straightforward to highlight its potential capabilities.

## Tech stack / Skills

### Programming Paradigms and Techniques

- Object-oriented programming (OOP)
- Type hints
- Generators
- Regular expressions

### Data Version Control and Storage

- dvc (with Azure Blob Storage)
- Git
- Azure Blob Storage

### Frameworks and Libraries

- FastAPI
- BeautifulSoup4
- Pydantic

### Development Tools

- Docker
- GitHub Actions
- .pre-commit hooks
- Static analysis tools

### Other

- Unit tests
- Logging
- Environment variables

## Deploy

### Deploy with docker (recommended)

With Access to Azure Blob Storage with Images:

1. Create `config.local` file in `.dvc/` directory and update it with your credentials for the image container following the `.dvc/config.local.template` file.
2. Run `dvc pull` to download data from Azure Blob Storage.
3. Run `docker load < docker_images/docker_image.tar` to load Docker image.
4. Create a `.env` file and update it with credentials for the container storing scraping results following the `.env.template` file.
5. Run `docker run -d --publish 8000:8000 --env-file .env housing_price_prediction` to run Docker container on port 8000.
6. Visit [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) to explore the API documentation. (Since swagger does not support Body in GET, for predictions you should use another tool such as Postman).


Without Access to Azure Blob Storage with Images (Azure Blob Storage still required):

1. Run `docker build -t housing_price_prediction  . ` to build docker image.
2. Create a `.env` file and update it with credentials for the container storing scraping results following the `.env.template` file.
3. Run `docker run -d --publish 8000:8000 --env-file .env housing_price_prediction` to run Docker container on port 8000.
4. Visit [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) to explore the API documentation. (Since swagger does not support Body in GET, for predictions you should use another tool such as Postman).

### Deploy locally

1. Install requirements from `requirements.txt` file.
2. Create a `.env` file and update it with credentials for the container storing scraping results following the `.env.template` file.
3. Run `docker run -d --publish 8000:8000 --env-file .env housing_price_prediction` to run Docker container on port 8000.
4. Visit [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) to explore the API documentation. (Since swagger does not support Body in GET, for predictions you should use another tool such as Postman).

## License

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg