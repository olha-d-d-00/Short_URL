import datetime
import json
import random
import pymongo

import aiofiles
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Annotated
import string

from starlette.responses import RedirectResponse

from funcs import Shortener

app = FastAPI()

templates = Jinja2Templates(directory="templates")

client = pymongo.AsyncMongoClient("mongodb://admin:password@localhost:27017/")
shortener_db = client["shortener_db"]
urls_collection = shortener_db["urls"]
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/")
async def create_short_url(long_url: Annotated[str, Form()]):
    short_url = await Shortener.create_short_url(urls_collection, long_url)
    return {"message": f"Your original URL: {long_url}, Short_url: http://127.0.0.1:8000/{short_url}"}



@app.get("/{short_url}")
async def url_redirect(short_url: str):
    final_urls_dict = await urls_collection.find_one({"short_url": short_url})
    if final_urls_dict:
        query_filter = {"short_url": short_url}
        await urls_collection.update_one(query_filter, {"$inc": {"counter_clicks": 1}})
        final_url = final_urls_dict.get("long_url")
        return RedirectResponse(final_url)
    return {"message": f"Error, no URL found for {short_url}"}
