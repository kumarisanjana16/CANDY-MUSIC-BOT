import os
import asyncio
import aiohttp
from youtube_search import YoutubeSearch

API_URL = os.environ.get("API_URL", "https://a60176-682e.d.onjrnm.link")
API_KEY = os.environ.get("API_KEY", "ZEXXY1NEXOR")
API_TYPE = os.environ.get("API_TYPE", "audio")
API_FORMAT = os.environ.get("API_FORMAT", "mp3")

# API ko gaana taiyaar karne me time lagta hai — 3 minute tak wait karte hain.
DOWNLOAD_TIMEOUT = int(os.environ.get("DOWNLOAD_TIMEOUT", "180"))

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)



async def search_youtube(query: str):
    """YouTube pe search karta hai, pehla result deta hai (raw dict, library format)."""
    loop = asyncio.get_event_loop()

    def _search():
        results = YoutubeSearch(query, max_results=1).to_dict()
        return results[0] if results else None

    return await loop.run_in_executor(None, _search)


async def search_track(query: str):
    """search_youtube ka normalized wrapper — id/title/duration/thumbnail/url deta hai."""
    result = await search_youtube(query)
    if not result:
        return None

    thumbnails = result.get("thumbnails") or []
    video_id = result.get("id")

    return {
        "id": video_id,
        "title": result.get("title", "Unknown"),
        "duration": result.get("duration", ""),
        "thumbnail": thumbnails[0] if thumbnails else None,
        "channel": result.get("channel") or result.get("uploader") or "",
        "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
    }


class DownloadError(Exception):
    """API se gaana download/ready nahi ho paya."""


def _video_id(video: str) -> str:
    """Poora YouTube link ya id — dono se sirf video id nikalta hai (API ko id chahiye)."""
    video = (video or "").strip()
    if not video:
        return ""
    if "youtu.be/" in video:
        video = video.split("youtu.be/")[1]
    elif "v=" in video:
        video = video.split("v=")[1]
    elif "/shorts/" in video:
        video = video.split("/shorts/")[1]
    elif "/embed/" in video:
        video = video.split("/embed/")[1]
    for sep in ("?", "&", "/", "#"):
        video = video.split(sep)[0]
    return video


def _extract_url(data) -> str | None:
    if isinstance(data, dict):
        for key in ("url", "download_url", "link", "audio_url", "file", "result"):
            value = data.get(key)
            if isinstance(value, str) and value.startswith("http"):
                return value
            if isinstance(value, dict):
                nested = _extract_url(value)
                if nested:
                    return nested
    return None


async def get_stream_url(video: str) -> str:
    """
    Download API se audio nikalta hai. API ko sirf video id jaati hai
    (jaise GX9x62kFsVU). Gaana ready hone tak wait karta hai
    (max DOWNLOAD_TIMEOUT = 3 minute), warna DownloadError.
    """
    video_id = _video_id(video)
    if not video_id:
        raise DownloadError("Video id nahi mila")

    params = {"url": video_id, "type": API_TYPE, "api_key": API_KEY}
    timeout = aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT, sock_read=DOWNLOAD_TIMEOUT)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{API_URL}/",
                params=params,
                allow_redirects=False,  # redirect mile to seedha wahi stream url
            ) as resp:
                if resp.status in (301, 302, 303, 307, 308):
                    location = resp.headers.get("Location")
                    if location:
                        return location

                if resp.content_type and "json" in resp.content_type:
                    data = await resp.json(content_type=None)
                    found = _extract_url(data)
                    if found:
                        return found
                    raise DownloadError(f"API response me url nahi mila: {data}")

                # API seedha audio file bhejta hai — poora download hone tak wait
                if resp.status == 200:
                    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{API_FORMAT}")
                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(131072):
                            f.write(chunk)
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        return file_path
                    raise DownloadError("Khali file mili")

                raise DownloadError(f"API ne unexpected response diya: {resp.status}")
    except asyncio.TimeoutError:
        raise DownloadError("Download timeout — 3 minute me gaana ready nahi hua")
    except aiohttp.ClientError as e:
        raise DownloadError(f"API tak pahunch nahi paaye: {e}")


async def get_related_track(title: str, exclude_id: str = None):
    """
    Autoplay ke liye — current gaane ke naam se milta-julta agla gaana dhoondta
    hai (youtube ke autoplay jaisa). Same video dobara na aaye iske liye
    `exclude_id` skip kar diya jaata hai.
    """
    loop = asyncio.get_event_loop()
    base = (title or "").split("|")[0].split("(")[0].strip()
    if not base:
        return None

    def _search():
        try:
            return YoutubeSearch(f"{base} song", max_results=8).to_dict()
        except Exception:
            return []

    results = await loop.run_in_executor(None, _search)
    for result in results or []:
        video_id = result.get("id")
        if not video_id or video_id == exclude_id:
            continue
        thumbnails = result.get("thumbnails") or []
        return {
            "id": video_id,
            "title": result.get("title", "Unknown"),
            "duration": result.get("duration", ""),
            "thumbnail": thumbnails[0] if thumbnails else None,
            "channel": result.get("channel") or result.get("uploader") or "",
            "url": f"https://www.youtube.com/watch?v={video_id}",
        }
    return None
