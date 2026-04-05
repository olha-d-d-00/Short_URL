import json
import random
from tempfile import template
from typing import Annotated

import aiofiles
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Annotated
import string

from starlette.responses import RedirectResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/")
async def create_short_url(long_url: Annotated[str, Form()]):

    available_characters = string.ascii_letters + string.digits

    async with aiofiles.open("urls.json", "r") as f:
        final_urls_dict = json.loads(await f.read())

    short_url = "".join([random.choice(available_characters) for _ in range(6+1)])
    while short_url in final_urls_dict:
        short_url = "".join([random.choice(available_characters) for _ in range(6+1)])

    final_urls_dict[short_url] = long_url

    async with aiofiles.open("urls.json", "w") as f:
        await f.write(json.dumps(final_urls_dict))

    return {"message": f"Your original URL: {long_url}, Short_url: http://127.0.0.1:8000/{short_url}"}

@app.get("/{short_url}")
async def url_redirect(short_url: str):
    async with aiofiles.open("urls.json", "r") as f:
        final_urls_dict = json.loads(await f.read())

    final_url = final_urls_dict.get(short_url)
    if final_url:
        return RedirectResponse(final_url)
    return {"message": f"Error, no URL found for {short_url}"}
