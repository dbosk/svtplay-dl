import http.client
import logging
import re
from html import unescape
from urllib.parse import urljoin

from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry
from svtplay_dl.utils.output import formatname
from svtplay_dl.utils.parser import Options

http.client._MAXHEADERS = 200

# Used for UA spoofing in get_http_data()
FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"

retry = Retry(total=5, read=5, connect=5, backoff_factor=0.3, status_forcelist=(500, 502, 504))


class HTTP(Session):
    """
    HTTP client session with custom configuration and retry logic.
    
    Extends requests.Session with application-specific settings including
    SSL verification, proxy support, custom headers, and automatic retries.
    """
    
    def __init__(self, config={}, *args, **kwargs):
        """
        Initialize HTTP session with configuration.
        
        Args:
            config: Configuration dictionary with ssl_verify, proxy, timeout,
                   http_headers, and cookies settings
            *args: Additional arguments for Session
            **kwargs: Additional keyword arguments for Session
        """
        Session.__init__(self, *args, **kwargs)
        adapter = HTTPAdapter(max_retries=retry)

        self.mount("http://", adapter)
        self.mount("https://", adapter)
        self.verify = config.get("ssl_verify")
        self.proxy = config.get("proxy")
        self.timeout = config.get("timeout")
        if config.get("http_headers"):
            self.headers.update(self.split_header(config.get("http_headers")))
        if config.get("cookies"):
            self.cookies.update(self.split_header(config.get("cookies")))
        self.headers.update({"User-Agent": FIREFOX_UA})

    def check_redirect(self, url):
        """
        Check if URL redirects and return final URL.
        
        Args:
            url: URL to check for redirects
            
        Returns:
            str: Final URL after following redirects
        """
        return self.get(url, stream=True).url

    def request(self, method, url, *args, **kwargs):
        headers = kwargs.pop("headers", None)
        if headers:
            for i in headers.keys():
                self.headers[i] = headers[i]
        else:
            if "Range" in self.headers:  # for some reason headers is always there for each request
                del self.headers["Range"]  # need to remove it because we dont want it
        logging.debug("HTTP getting %r", url)
        res = Session.request(self, method, url, verify=self.verify, proxies=self.proxy, timeout=self.timeout, *args, **kwargs)
        return res

    def split_header(self, headers):
        """
        Parse semicolon-separated header string into dictionary.
        
        Args:
            headers: String of headers in format "key1=value1;key2=value2"
            
        Returns:
            dict: Parsed headers as key-value pairs
        """
        return dict(x.split("=") for x in headers.split(";") if x)


def download_thumbnails(output, config, urls):
    """
    Download thumbnail images for video content.
    
    Downloads show and episode thumbnails, saving them with appropriate
    naming conventions.
    
    Args:
        output: Output configuration dictionary with metadata
        config: Configuration object with output path settings
        urls: List of tuples (is_show: bool, url: str) for thumbnails to download
    """
    for show, url in urls:
        if "&amp;" in url:
            url = unescape(url)
        data = Session().get(url).content
        loutout = output.copy()
        loutout["ext"] = "tbn"
        if show:
            # Config for downloading show thumbnail
            cconfig = Options()
            cconfig.set("output", config.get("output"))
            cconfig.set("path", config.get("path"))
            cconfig.set("subfolder", config.get("subfolder"))
            cconfig.set("filename", "{title}.tvshow.{ext}")
        else:
            cconfig = config

        filename = formatname(loutout, cconfig)
        logging.info("Thumbnail: %s", filename)

        with open(filename, "wb") as fd:
            fd.write(data)


def get_full_url(url, srcurl):
    """
    Resolve relative URL to absolute URL using source URL as base.
    
    Handles absolute URLs, root-relative URLs, and path-relative URLs.
    
    Args:
        url: URL to resolve (may be relative or absolute)
        srcurl: Source/base URL to resolve against
        
    Returns:
        str: Absolute URL
    """
    if url[:4] == "http":
        return url
    if url[0] == "/":
        baseurl = re.search(r"^(http[s]{0,1}://[^/]+)/", srcurl)
        return f"{baseurl.group(1)}{url}"

    # remove everything after last / in the path of the URL
    baseurl = re.sub(r"^([^\?]+)/[^/]*(\?.*)?$", r"\1/", srcurl)
    returl = urljoin(baseurl, url)

    return returl
