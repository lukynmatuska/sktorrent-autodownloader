"""Module for download torrents from SkTorrent"""

import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup


SKTORRENT_URL = "https://sktorrent.eu"
REQUEST_TIMEOUT = 5
DOWNLOAD_IN_SLOVAK = "STIAHNUT"
# pylint: disable=line-too-long
TMP_URL = "https://sktorrent.eu/torrent/details.php?name=Survivor-%C4%8Cesko-&-Slovensko-S03E16-2024-WEB-DL-1080p-CSFD-24%&id=c55d277938775ef755ca8697d9001115fbe5b4c2"


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

    # def download_torrent(self):
    #     """Function to download the torrent file"""
    #     pass

    def get_torrent_links_from_page(self, page_url: str = TMP_URL):
        """Function to parse """
        torrent_page = self.get_page(page_url)
        soup = BeautifulSoup(torrent_page.text, "html.parser")
        # print(soup)
        # return soup.select_one('body > center > table:nth-child(2) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > div > table:nth-child(3) > tbody > tr:nth-child(2) > td:nth-child(5) > a')
        return soup.find_all(
            "a",
            string = DOWNLOAD_IN_SLOVAK
        )


if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    skt = SkTorrentDownloader()
    skt.login()
