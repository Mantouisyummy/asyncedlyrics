"""Utility functions for `asyncedlyrics` package"""

from dataclasses import dataclass
from bs4 import BeautifulSoup, FeatureNotFound
import rapidfuzz
from typing import Union, Callable, Optional
import datetime
from enum import Enum, auto
import re
import aiohttp
import os
from pathlib import Path

R_FEAT = re.compile(r"\((feat.+)\)", re.IGNORECASE)


class TargetType(Enum):
    PLAINTEXT = auto()
    PREFER_SYNCED = auto()
    SYNCED_ONLY = auto()


@dataclass
class Lyrics:
    synced: Optional[str] = None
    unsynced: Optional[str] = None

    def add_unknown(self, unknown: str):
        type = identify_lyrics_type(unknown)
        if type == "synced":
            self.synced = unknown
        elif type == "plaintext":
            self.unsynced = unknown

    def update(self, other: Optional["Lyrics"]):
        if not other:
            return
        if other.synced:
            self.synced = other.synced
        if other.unsynced:
            self.unsynced = other.unsynced

    def is_preferred(self, target_type: TargetType) -> bool:
        return bool(
            self.synced or (target_type == TargetType.PLAINTEXT and self.unsynced)
        )

    def is_acceptable(self, target_type: TargetType) -> bool:
        return bool(
            self.synced or (target_type != TargetType.SYNCED_ONLY and self.unsynced)
        )

    def to_str(self, target_type: TargetType) -> str:
        if target_type == TargetType.PLAINTEXT:
            return self.unsynced or synced_to_plaintext(self.synced)
        elif target_type == TargetType.PREFER_SYNCED:
            return self.synced or self.unsynced
        return self.synced

    def save_lrc_file(self, path: str, target_type: TargetType):
        """Saves the `.lrc` file"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_str(target_type))


def get_cache_path(lib_name: str = "asyncedlyrics", auto_create: bool = True) -> Path:
    """Get or create a cache directory for the given library name."""
    if os.name == "nt":  # Windows
        base_dir = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
    elif os.name == "posix":
        if "Darwin" in os.uname().sysname:  # macOS
            base_dir = os.path.expanduser("~/Library/Caches")
        else:  # Linux
            base_dir = os.path.expanduser("~/.cache")
    else:
        base_dir = os.path.expanduser("~")
    target_dir = Path(base_dir) / lib_name
    if auto_create:
        target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def synced_to_plaintext(synced_lyrics: str) -> str:
    return re.sub(r"\[\d+:\d+\.\d+\] ", "", synced_lyrics)


def identify_lyrics_type(lrc: str) -> str:
    """Identifies the type of the LRC string"""
    if not lrc:
        return "invalid"
    lines = lrc.split("\n")[5:10]
    if all("[" in l for l in lines):
        return "synced"
    return "plaintext"


def has_translation(lrc: str) -> bool:
    """Checks whether the LRC string has a translation or not"""
    lines = lrc.split("\n")[5:10]
    for i, line in enumerate(lines):
        if "[" in line:
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if "(" not in next_line:
                    return False
    return True


async def generate_bs4_soup(url: str, **kwargs):
    """Returns a `BeautifulSoup` from the given `url`.
    Tries to use `lxml` as the parser if available, otherwise `html.parser`
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as r:
                try:
                    soup = BeautifulSoup(await r.text(), features="lxml", **kwargs)
                except FeatureNotFound:
                    soup = BeautifulSoup(await r.text(), features="html.parser", **kwargs)
                return soup
        finally:
            await session.close()


def format_time(time_in_seconds: float):
    """Returns a [mm:ss.xx] formatted string from the given time in seconds."""
    time = datetime.timedelta(seconds=time_in_seconds)
    minutes, seconds = divmod(time.seconds, 60)
    return f"{minutes:02}:{seconds:02}.{time.microseconds // 10000:02}"


def str_score(a: str, b: str) -> float:
    """Returns the similarity score of the two strings"""
    # if user does not specify any "feat" in the search term,
    # remove the "feat" from the search results' names
    a, b = a.lower(), b.lower()
    if "feat" not in b:
        a, b = R_FEAT.sub("", a), R_FEAT.sub("", b)
    return rapidfuzz.fuzz.token_set_ratio(a, b)


def str_same(a: str, b: str, n: int) -> bool:
    """Returns `True` if the similarity score of the two strings is greater than `n`"""
    return round(str_score(a, b)) >= n


def sort_results(
        results: list,
        search_term: str,
        compare_key: Union[str, Callable[[dict], str]] = "name",
) -> list:
    """
    Sorts the API results based on the similarity score of the `compare_key` with
    the `search_term`.

    ## Parameters
    - `results`: The API results
    - `search_term`: The search term
    - `compare_key`: The key to compare the `search_term` with. Can be a string or a
    function that takes a track and returns a string.
    """
    if isinstance(compare_key, str):
        def compare_key(t):
            return t[compare_key]

    def sort_key(t):
        return str_score(compare_key(t), search_term)

    return sorted(results, key=sort_key, reverse=True)


def get_session(netease: bool = False) -> aiohttp.ClientSession:
    if netease:
        headers_text = (
            "NMTID=00OAVK3xqDG726ITU6jopU6jF2yMk0AAAGCO8l1BA; JSESSIONID-WYYY=8KQo11YK2GZP45RMlz8Kn80vHZ9%2FGvwzRKQXXy0iQoFKycWdBlQjbfT0MJrFa6hwRfmpfBYKeHliUPH287JC3hNW99WQjrh9b9RmKT%2Fg1Exc2VwHZcsqi7ITxQgfEiee50po28x5xTTZXKoP%2FRMctN2jpDeg57kdZrXz%2FD%2FWghb%5C4DuZ%3A1659124633932; _iuqxldmzr_=32; _ntes_nnid=0db6667097883aa9596ecfe7f188c3ec,1659122833973; _ntes_nuid=0db6667097883aa9596ecfe7f188c3ec; WNMCID=xygast.1659122837568.01.0; WEVNSM=1.0.0; WM_NI=CwbjWAFbcIzPX3dsLP%2F52VB%2Bxr572gmqAYwvN9KU5X5f1nRzBYl0SNf%2BV9FTmmYZy%2FoJLADaZS0Q8TrKfNSBNOt0HLB8rRJh9DsvMOT7%2BCGCQLbvlWAcJBJeXb1P8yZ3RHA%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee90c65b85ae87b9aa5483ef8ab3d14a939e9a83c459959caeadce47e991fbaee82af0fea7c3b92a81a9ae8bd64b86beadaaf95c9cedac94cf5cedebfeb7c121bcaefbd8b16dafaf8fbaf67e8ee785b6b854f7baff8fd1728287a4d1d246a6f59adac560afb397bbfc25ad9684a2c76b9a8d00b2bb60b295aaafd24a8e91bcd1cb4882e8beb3c964fb9cbd97d04598e9e5a4c6499394ae97ef5d83bd86a3c96f9cbeffb1bb739aed9ea9c437e2a3; WM_TID=AAkRFnl03RdABEBEQFOBWHCPOeMra4IL; playerid=94262567"
        )
        return aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(sock_connect=5, sock_read=20),
                                     headers={"cookie": headers_text})
    else:
        return aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(sock_connect=5, sock_read=20))


def get_best_match(
        results: list,
        search_term: str,
        compare_key: Union[str, Callable[[dict], str]] = "name",
        min_score: int = 65,
) -> Optional[dict]:
    """
    Returns the best match from the API results based on the similarity score of the `compare_key`
    with the `search_term`.
    """
    if not results:
        return None
    results = sort_results(results, search_term, compare_key=compare_key)
    best_match = results[0]

    value_to_compare = (
        best_match[compare_key]
        if isinstance(compare_key, str)
        else compare_key(best_match)
    )
    if not str_same(value_to_compare, search_term, n=min_score):
        return None
    return best_match
