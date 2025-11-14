from pipelines.cna_etl import CNA_ETL
from pipelines.udn_etl import UDN_ETL
from utils.constants import SCRAPER_SETTINGS

import asyncio
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import uvicorn
# from fastapi import FastAPI, BackgroundTasks


async def main():

    tasks = [
        asyncio.to_thread(UDN_ETL),
        asyncio.to_thread(CNA_ETL)
    ]

    await asyncio.gather(*tasks)


# app = FastAPI()

# @app.get("/cna_scrape")
# async def cna_scrape(background_tasks: BackgroundTasks):
#     background_tasks.add_task(CNA_ETL)

if __name__ == "__main__":
    asyncio.run(main())
    
#     uvicorn.run(app, host="0.0.0.0", port=8000)