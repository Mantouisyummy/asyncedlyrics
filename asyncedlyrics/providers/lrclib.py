"""Lrclib (lrclib.net) LRC provider"""

from typing import Optional, Any, Coroutine
from .base import LRCProvider
from ..utils import Lyrics, sort_results
import aiohttp

class Lrclib(LRCProvider):
    """Lrclib LRC provider class"""

    ROOT_URL = "https://lrclib.net"
    API_ENDPOINT = ROOT_URL + "/api"
    SEARCH_ENDPOINT = API_ENDPOINT + "/search"
    LRC_ENDPOINT = API_ENDPOINT + "/get/"

    def __init__(self) -> None:
        super().__init__()
        self.session = aiohttp.ClientSession()

    async def get_lrc_by_id(self, track_id: str) -> Optional[Lyrics]:
        url = self.LRC_ENDPOINT + track_id
        session = await self.get_session()
        async with session.get(url) as r:
            if not r.ok:
                return None
            track = await r.json()
            lrc = Lyrics()
            lrc.synced = track.get("syncedLyrics")
            lrc.unsynced = track.get("plainLyrics")
            return lrc

    async def get_lrc(self, search_term: str) -> Coroutine[Any, Any, Lyrics | None] | None:
        url = self.SEARCH_ENDPOINT
        session = await self.get_session()
        async with session.get(url, params={"q": search_term}) as r:
            if not r.ok:
                return None
            tracks = await r.json()
            if not tracks:
                return None
            tracks = sort_results(
                tracks, search_term, lambda t: f'{t["artistName"]} - {t["trackName"]}'
            )
            _id = str(tracks[0]["id"])
            return await self.get_lrc_by_id(_id)