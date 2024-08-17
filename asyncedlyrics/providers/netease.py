"""NetEase (music.163.com) china-based provider"""
import json
from typing import Optional, Any, Coroutine
from .base import LRCProvider
from ..utils import Lyrics, get_best_match
import aiohttp

class NetEase(LRCProvider):
    """NetEase provider class"""

    API_ENDPOINT_METADATA = "https://music.163.com/api/search/pc"
    API_ENDPOINT_LYRICS = "https://music.163.com/api/song/lyric"

    def __init__(self) -> None:
        super().__init__()

    async def search_track(self, search_term: str) -> Optional[dict]:
        """Returns a `dict` containing some metadata for the found track."""
        params = {"limit": 10, "type": 1, "offset": 0, "s": search_term}
        session = await self.get_session(netease=True)
        async with session.get(self.API_ENDPOINT_METADATA, params=params) as response:
            try:
                results = (await response.json()).get("result", {}).get("songs")
            except aiohttp.ContentTypeError:
                text = await response.text()
                results = json.loads(text).get("result", {}).get("songs")

            if not results:
                return None
            cmp_key = lambda t: f"{t.get('name')} {t.get('artists')[0].get('name')}"
            track = get_best_match(results, search_term, cmp_key)
            # Update the session cookies from the new sent cookies for the next request.
            session.cookie_jar.update_cookies(response.cookies)
            session.headers.update({"referer": str(response.url)})
            return track

    async def get_lrc_by_id(self, track_id: str) -> Optional[Lyrics]:
        params = {"id": track_id, "lv": 1}
        session = await self.get_session()
        async with session.get(self.API_ENDPOINT_LYRICS, params=params) as response:
            try:
                lrc_data = (await response.json()).get("lrc", {}).get("lyric")
            except aiohttp.ContentTypeError:
                text = await response.text()
                lrc_data = json.loads(text).get("lrc", {}).get("lyric")

            lrc = Lyrics()
            lrc.add_unknown(lrc_data)
            return lrc

    async def get_lrc(self, search_term: str) -> Coroutine[Any, Any, Optional[Lyrics]] | None:
        track = await self.search_track(search_term)
        if not track:
            return None
        return await self.get_lrc_by_id(track["id"])