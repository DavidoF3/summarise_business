# Summarise Business

## Task criteria
- The API must incorporate an endpoint that accepts data from a 10-K filing report and subsequently returns a response that includes summary of the business description.

- The solution design must be flexible enough to accommodate easy switching of models, and the addition of new models in the future.

- The solution must be able to run on any machine, locally or in the cloud.

- The solution must be documented and easy to understand.


## Setup

Move into the repository and ensure that Docker has been installed in your system (necessary to make the app runnable locally or in the cloud).

Before running the API make sure that the configuration inputs are appropriately setup. To do so, open the file ```config.yaml``` and define the following fields:

```yaml
edgar_identity: <Name_and_surname> <email_address>
edgar_form: <form_type e.g. "10-K">
summariser_checkpoint: <huggingface_summariser_checkpoint>
```

Then build and run the services: a MongoDB database (named mongodb) and a FastAPI app (named fastapi_app) to create or query a company description summary.

```
docker compose up -d mongodb
docker compose build
docker compose up fastapi_app
```

Once the app is running, you can access two different endpoints:

- ```http://127.0.0.1:4000/summarise/<company_name>```: Add the ticker name of the company that you are interested in and this endpoint will create a summary of its description and store it in a MongoDB database.

- ```http://127.0.0.1:4000/summaries/<company_name>```: Add the ticker name of the company that you are interested in and a summary about this company gets searched in the the MongoDB databease. If a summary is available, it gets returned.

To locally view the reults in the database, you need to install MongoDB Compass.

## Testing

Want to know the descriptions of some of the largest technology companies? Try running the ```/summarise/``` endpoint on the company tickers listed below.

- AAPL
- AMZN
- DELL
- GOOGL
- IBM 
- META
- MSFT
- NFLX
- NVDA
- TSLA

If at some other point in the future you want to query their summaries again, run the ```/sumaries/``` endpoint on any of the tickers above. This endpoint will return their summaries more quickly because they will get retrieved from the databased, rather than get recomputed.