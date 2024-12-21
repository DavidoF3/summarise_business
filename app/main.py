import os
from typing import Any

import uvicorn
import yaml
from edgar import Company, set_identity
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from transformers import pipeline


class DBinfo(BaseModel, validate_assignment=True):
    db_url: str
    db_name: str
    collection_name: str


class CompanySummary(BaseModel, validate_assignment=True):
    company: str
    summary: str


class InferConfig(BaseModel, validate_assignment=True):
    edgar_identity: str
    edgar_form: str
    summariser_checkpoint: str


def get_db_info() -> DBinfo:
    db_info = DBinfo(
        db_url=os.environ["DB_URL"],
        db_name=str(os.environ["DB_NAME"]),
        collection_name=str(os.environ["COLLECTION_NAME"]),
    )
    return db_info


def fetch_company_summary(company_name: str, cfg_infer: InferConfig) -> CompanySummary:
    try:
        set_identity(cfg_infer.edgar_identity)
        filing = Company(company_name).get_filings(form=cfg_infer.edgar_form).latest(1)
        tenq = filing.obj()
        business_description = tenq.business[:1024]
        summariser = pipeline("summarization", model=cfg_infer.summariser_checkpoint)
        summary = summariser(business_description, max_length=200, min_length=50, do_sample=False)

        company_summary = CompanySummary(company=company_name, summary=summary[0]["summary_text"])
        return company_summary
    except AttributeError as exc:
        raise Exception(f"Company {company_name} not found") from exc


def save_summary_to_db(
    company_summary: CompanySummary,
    db_info: DBinfo,
) -> None:
    client: MongoClient = MongoClient(db_info.db_url)
    db = client[db_info.db_name]
    collection = db[db_info.collection_name]
    result = collection.insert_one(company_summary.model_dump())
    print(result)
    client.close()


def get_file_from_db(
    company_name: str,
    db_info: DBinfo,
) -> Any:
    client: MongoClient = MongoClient(db_info.db_url)
    db = client[db_info.db_name]
    collection = db[db_info.collection_name]
    try:
        company_info = collection.find_one({"company": {"$regex": company_name}})
        assert company_info is not None
    except AssertionError as exc:
        raise Exception(
            f"Summary for {company_name} does not exist"
        ) from exc
    client.close()
    return company_info


app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "You are in Argo's company summarisation API"}


@app.get("/summarise/{company_name}")
def summarize_company(company_name: str) -> dict[str, str]:
    try:
        with open("config.yaml") as f:
            cfg = yaml.safe_load(f)

        cfg_infer = InferConfig(**cfg)
        company_summary = fetch_company_summary(company_name, cfg_infer)
        db_info = get_db_info()
        save_summary_to_db(company_summary, db_info)
        return {"company_name": company_summary.company, "summary": company_summary.summary}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/summaries/{company_name}")
def get_summaries(
    company_name: str,
) -> dict[str, str]:
    try:
        db_info = get_db_info()
        company_summary = get_file_from_db(company_name, db_info)
        return {"company_name": company_summary["company"], "summary": company_summary["summary"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)
