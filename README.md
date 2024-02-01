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