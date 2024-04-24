"""Module for download torrents from SkTorrent"""

import json
import os
import time
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup


SKTORRENT_URL = "https://sktorrent.eu"
REQUEST_TIMEOUT = 5
DOWNLOAD_IN_SLOVAK = "STIAHNUT"
# pylint: disable=line-too-long
SKTORRENT_DEFAULT_PAGE_URL = "https://sktorrent.eu/torrent/details.php?name=Survivor-%C4%8Cesko-&-Slovensko-S03E16-2024-WEB-DL-1080p-CSFD-24%&id=c55d277938775ef755ca8697d9001115fbe5b4c2"
ONE_MINUTE = 60


class SkTorrentDownloader:
    """Class for easy download torrents from Slovak portal"""

    def __init__(
        self,
        username=os.getenv("SKTORRENT_USERNAME"),
        password=os.getenv("SKTORRENT_PASSWORD")
    ) -> None:
        self.username = username
        self.password = password
        self.request_session = requests.Session()

        # Setup proxies for our session
        proxies = os.getenv("REQUESTS_PROXIES", "")
        if proxies != "":
            self.request_session.proxies = json.loads(proxies)

    def login(self):
        """Function to login into portal"""
        login_url = "/torrent/login.php?returnto=index.php"

        return self.request_session.post(
            SKTORRENT_URL + login_url,
            {
                "uid": self.username,
                "pwd": self.password
            },
            timeout = REQUEST_TIMEOUT
        )

    def get_page(self, *args, **kwargs):
        """Function to return GET request with session"""
        return self.request_session.get(*args, **kwargs)

    def download_torrent(self, torrent_url):
        """Function to download the torrent file"""
        torrent_request = self.request_session.get(torrent_url)
        return torrent_request.content

    def get_torrent_links_from_page(self, page_url: str = SKTORRENT_DEFAULT_PAGE_URL):
        """Function to parse """
        torrent_page = self.get_page(page_url)
        soup = BeautifulSoup(torrent_page.text, "html.parser")
        return soup.find_all(
            "a",
            string = DOWNLOAD_IN_SLOVAK
        )

    def get_episode_link(
        self,
        episode: str = "S03E18",
        page_url: str = SKTORRENT_DEFAULT_PAGE_URL
    ) -> str:
        """Function to get link to episode torrent file"""
        links = self.get_torrent_links_from_page(page_url)
        for link in links:
            if episode in link["href"]:
                return SKTORRENT_URL + link["href"]
        return None

    def get_episode_link_loop(
        self,
        episode: str = "S03E18",
        page_url: str = SKTORRENT_DEFAULT_PAGE_URL,
        sleep_time: int = ONE_MINUTE,
        verbose: bool = False
    ) -> str:
        """Function to get link to episode torrent file in loop"""
        while True:
            if verbose:
                print(f"Going to get link for episode '{episode}'.")
            episode_link = self.get_episode_link(episode, page_url)
            if episode_link is not None:
                if verbose:
                    print(f"Found link for episode '{episode}'.")
                return episode_link
            elif verbose:
                print(f"Not found link for episode '{episode}', going to wait for {sleep_time} seconds.")
            time.sleep(sleep_time)

if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    skt = SkTorrentDownloader()
    skt.login()
