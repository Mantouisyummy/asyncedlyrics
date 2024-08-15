"""Some simple tests for geting notifed for API changes of the providers"""

import os
import asyncedlyrics
import logging

import pytest

logging.basicConfig(level=logging.DEBUG)

q = os.getenv("TEST_Q", "bad guy billie eilish")


@pytest.mark.asyncio
async def _test_provider(provider: str, **kwargs):
    lrc = await asyncedlyrics.search(search_term=q, providers=[provider], **kwargs)
    logging.debug(lrc)
    assert isinstance(lrc, str)
    return lrc


@pytest.mark.asyncio
async def test_netease():
    await _test_provider("NetEase")


@pytest.mark.asyncio
async def test_musixmatch():
    await _test_provider("Musixmatch")


@pytest.mark.asyncio
async def test_musixmatch_translation():
    lrc = await _test_provider("Musixmatch", lang="es")
    # not only testing there is a result, but the translation is also included
    assert asyncedlyrics.utils.has_translation(lrc)


@pytest.mark.asyncio
async def test_musixmatch_enhanced():
    await _test_provider("Musixmatch", enhanced=True)


@pytest.mark.asyncio
async def test_lrclib():
    await _test_provider("Lrclib")


@pytest.mark.asyncio
async def test_genius():
    await _test_provider("Genius")


@pytest.mark.asyncio
async def test_plaintext_only():
    lrc = await _test_provider("Lrclib", plain_only=True)
    assert asyncedlyrics.utils.identify_lyrics_type(lrc) == "plaintext"


@pytest.mark.asyncio
async def test_synced_only():
    lrc = await _test_provider("Lrclib", synced_only=True)
    assert asyncedlyrics.utils.identify_lyrics_type(lrc) == "synced"

# Not working (at least temporarily)
# def test_deezer():
#     _test_provider("Deezer")


# Fails randomly on CI
# def test_megalobiz():
#     _test_provider("Megalobiz")
