import requests
import xml.etree.ElementTree as ET

CHANNEL_ID = "UCXRlIK3Cw_TJIQC5kSJJQMg"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

def fetch_latest_videos(max_results=10):
    try:
        response = requests.get(RSS_URL)
        response.raise_for_status()
    except Exception as e:
        print("RSS取得エラー:", e)
        return []

    root = ET.fromstring(response.content)

    # ★ YouTube RSS の正しい namespace
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/"
    }

    videos = []

    # ★ entry は atom:entry で取る必要がある
    for entry in root.findall("atom:entry", ns)[:max_results]:
        try:
            title = entry.find("atom:title", ns).text
            video_id = entry.find("yt:videoId", ns).text
            thumbnail = entry.find("media:group/media:thumbnail", ns).attrib["url"]

            videos.append({
                "title": title,
                "videoId": video_id,
                "thumbnail": thumbnail
            })
        except Exception as e:
            print("パースエラー:", e)

    print("RSS URL =", RSS_URL)
    print("videos =", videos)
    return videos