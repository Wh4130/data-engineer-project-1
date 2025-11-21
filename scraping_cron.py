from pipelines.cna_etl import CNA_ETL
from pipelines.udn_etl import UDN_ETL
from pipelines.ltn_etl import LTN_ETL
from utils.email_sender import EmailSender

import asyncio
import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import datetime as dt


# * --------------------------------------------------------------------------------
# --- FastAPI 寫法
"""
deployment: a webservice hosted on render
outside trigger > async scraping > load to mongodb > send email

$ failed! render disabled smtp email sender since 2025 September!
"""
"""
import uvicorn
from fastapi import FastAPI, BackgroundTasks, Query

app = FastAPI()

@app.get("/start_cna_etl")
async def start_cna_etl(background_tasks: BackgroundTasks,
                    k: str = Query('25', description = "factor k for clicking more button. should be a integer like string"),
                    t: str = Query('0.1', description = "factor t for waiting time. should be a float like string")
                    ):

    logging.info("start CNA ETL process")

    k = int(k)
    t = float(t)

    background_tasks.add_task(CNA_ETL, k, t)

    return {"message": "ETL process started in background"}

@app.get("/start_udn_etl")
async def start_udn_etl(background_tasks: BackgroundTasks,
                    k: str = Query('25', description = "factor k for clicking more button. should be a integer like string"),
                    t: str = Query('0.1', description = "factor t for waiting time. should be a float like string")
                    ):
    
    logging.info("start UDN ETL process")
    
    k = int(k)
    t = float(t)

    background_tasks.add_task(UDN_ETL, k, t)

    return {"message": "ETL process started in background"}
"""


# * --------------------------------------------------------------------------------
# --- Cronjob 寫法
"""
deployment: a cronjob hosted on render
cronjob trigger > async scraping then gather > load to mongodb > send email

$ adopted! cost 1 usd per month.
"""

async def main():

    tasks = [
        asyncio.to_thread(UDN_ETL),
        asyncio.to_thread(CNA_ETL),
        asyncio.to_thread(LTN_ETL)
    ]

    tasks_results = await asyncio.gather(*tasks)
    results = {
        "udn": tasks_results[0],
        "cna": tasks_results[1],
        "ltn": tasks_results[2]

    }
    

    print(EmailSender.send(os.getenv("RECIPIENT"), EmailSender.template(results)))


if __name__ == "__main__":
    asyncio.run(main())
    
    