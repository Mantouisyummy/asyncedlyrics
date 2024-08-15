# asyncedlyrics
 A fork of [Syncedlyrics](https://github.com/moehmeni/syncedlyrics). Asynchronous Get an LRC format lyrics for your music.

## Installation
```
pip install git+https://github.com/Mantouisyummy/asyncedlyrics.git
```
## Usage
### CLI
```
asyncedlyrics "SEARCH_TERM"
```

By default, this will prefer time synced lyrics, but use plaintext lyrics, if no synced lyrics are available.
To only allow one type of lyrics specify `--plain-only` or `--synced-only` respectively.

#### Available Options
| Flag | Description |
| --- | --- |
| `-o` | Path to save `.lrc` lyrics, default="{search_term}.lrc" |
| `-p` | Space-separated list of [providers](#providers) to include in searching |
| `-l` | Language code of the translation ([ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) format) |
| `-v` | Use this flag to show the logs |
| `--plain-only` | Only look for plain text (not synced) lyrics |
| `--synced-only` | Only look for synced lyrics |
| `--enhanced` | Searches for an [Enhanced](https://en.wikipedia.org/wiki/LRC_(file_format)#A2_extension:_word_time_tag) (word-level karaoke) format. If it isn't available, search for regular synced lyrics.

### Python
```py
# This simple
lrc = await asyncedlyrics.search("[TRACK_NAME] [ARTIST_NAME]")

# Or with options:
await asyncedlyrics.search("...", plain_only=True, save_path="{search_term}_1234.lrc", providers=["NetEase"])

# Get a translation along with the original lyrics (separated by `\n`):
await asyncedlyrics.search("...", lang="de")

# Get a word-by-word (karaoke) synced-lyrics if available
await asyncedlyrics.search("...", enhanced=True)
```

## Providers
- [Musixmatch](https://www.musixmatch.com/)
- ~~[Deezer](https://deezer.com/)~~ (Currently not working anymore)
- [Lrclib](https://github.com/tranxuanthang/lrcget/issues/2#issuecomment-1326925928)
- [NetEase](https://music.163.com/)
- [Megalobiz](https://www.megalobiz.com/)
- [Genius](https://genius.com) (For plain format)
- ~~[Lyricsify](https://www.lyricsify.com/)~~ (Broken duo to Cloudflare protection)

Feel free to suggest more providers or make PRs to fix the broken ones.

## License
[MIT](https://github.com/Mantouisyummy/asyncedlyrics/blob/master/LICENSE)

