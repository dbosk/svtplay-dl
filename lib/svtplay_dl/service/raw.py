import os
import re

from svtplay_dl.fetcher.dash import dashparse
from svtplay_dl.fetcher.hls import hlsparse
from svtplay_dl.service import Service


class Raw(Service):
    """
    Service handler for downloading raw media files (M3U8 and MPD).
    
    Handles direct URLs to HLS playlist (.m3u8) and DASH manifest (.mpd) files.
    """
    
    def get(self):
        """
        Process raw media URL and yield media streams.
        
        Detects the type of media file (HLS or DASH) and delegates to appropriate parser.
        
        Yields:
            VideoRetriever: Media stream objects for downloading
        """
        filename = os.path.basename(self.url[: self.url.rfind("/")])
        self.output["title"] = filename

        if re.search(".m3u8", self.url):
            yield from hlsparse(self.config, self.http.request("get", self.url), self.url, output=self.output)

        if re.search(".mpd", self.url):
            yield from dashparse(self.config, self.http.request("get", self.url), self.url, output=self.output)
