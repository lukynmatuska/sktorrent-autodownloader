"""Main module"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from qbittorrent import Client
from .features.git import Git
from .features.sktdownloader import SkTorrentDownloader, SKTORRENT_DEFAULT_PAGE_URL


load_dotenv()  # take environment variables from .env.
app = FastAPI(
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "persistAuthorization": True,
        "tryItOutEnabled": True,
    },
    title="SkTorent Autodownloader",
    description="REST API for easy torrent downloading",
)

origins = json.loads(os.getenv('CORS_ORIGINS'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.head("/")
async def root():
    """Root function"""
    git = Git()
    return {
        "git": git.short_hash(),
        "message": "Hello World",
        "time": datetime.now()
    }

@app.get("/health-check")
def health_check():
    """Function for docker health check"""
    return "success"


@app.get("/skt/page/")
def skt_page(
    page:str = SKTORRENT_DEFAULT_PAGE_URL,
    episode:str = "S03E16",
    category:str = "Survivor"
):
    """Function to download the torrent"""

    # Login to qBittorent
    qb = Client(os.getenv("QBT_URL", "localhost"))
    qb.login(
        os.getenv("QBT_LOGIN"), # username
        os.getenv("QBT_PASSWORD"), # password
    )

    # Init SkTorrent
    skt = SkTorrentDownloader()
    skt.login()

    # Begin process
    torrent_url = skt.get_episode_link(episode, page)
    if torrent_url is None:
        return HTTPException(
            status_code=404,
            detail="Link not found."
        )
    torrent_file = skt.download_torrent(torrent_url)
    res = qb.download_from_file(
        file_buffer=torrent_file,
        category=category
    )
    if res == "Fails.":
        return HTTPException(
            status_code=500,
            detail=f"500 {res}"
        )
    return "200"

@app.get("/skt/page/loop")
def skt_page_loop(
    page:str = SKTORRENT_DEFAULT_PAGE_URL,
    episode:str = "S03E18",
    verbose:bool = False,
    category:str = "Survivor"
):
    """Function to download the torrent with loop"""

    # Login to qBittorent
    qb = Client(os.getenv("QBT_URL", "localhost"))
    qb.login(
        os.getenv("QBT_LOGIN"), # username
        os.getenv("QBT_PASSWORD"), # password
    )

    # Init SkTorrent
    skt = SkTorrentDownloader()
    skt.login()

    # Begin process
    torrent_url = skt.get_episode_link_loop(episode, page, verbose=verbose)
    torrent_file = skt.download_torrent(torrent_url)
    res = qb.download_from_file(
        file_buffer=torrent_file,
        category=category
    )
    if res == "Fails.":
        return HTTPException(
            status_code=500,
            detail=f"500 {res}"
        )
    return "200"
