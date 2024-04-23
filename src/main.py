"""Main module"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qbittorrent import Client
from .features.git import Git
from .features.sktdownloader import SkTorrentDownloader, SKTORRENT_URL


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
def skt_page():
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
    links = skt.get_torrent_links_from_page()
    for link in links:
        if "S03E16" in link["href"]:
            torrent_url = SKTORRENT_URL + link["href"]
            torrent_request = skt.request_session.get(torrent_url)
            print(torrent_request)
            torrent_file = torrent_request.content
            with open('my-torrent-file.torrent', 'wb') as tf:
                tf.write(torrent_file)
            with open('my-torrent-file.torrent', 'rb') as tf:
                print(qb.download_from_file(tf))
            return "200"
    return "404"
