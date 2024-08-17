from typing import Optional
from .base import LRCProvider
from ..utils import Lyrics, generate_bs4_soup

class Genius(LRCProvider):
    """Genius provider class"""

    SEARCH_ENDPOINT = "https://genius.com/api/search/multi"

    async def get_lrc(self, search_term: str) -> Optional[Lyrics]:
        params = {"q": search_term, "per_page": 5}
        cookies = {
            "obuid": "e3ee67e0-7df9-4181-8324-d977c6dc9250",
        }
        session = await self.get_session()
        async with session.get(self.SEARCH_ENDPOINT, params=params, cookies=cookies) as r:
            if not r.ok:
                return None
            data = await r.json()
            data = data["response"]["sections"][1]["hits"]
            if not data:
                return None
            url = data[0]["result"]["url"]
            soup = await generate_bs4_soup(url)
            els = soup.find_all("div", attrs={"data-lyrics-container": True})
            if not els:
                return None
            lrc_str = ""
            for el in els:
                lrc_str += el.get_text(separator="\n", strip=True).replace("\n[", "\n\n[")
            lrc = Lyrics()
            lrc.unsynced = lrc_str
            return lrc
