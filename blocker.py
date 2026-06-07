import config


class Blocker:
    def __init__(self, url: str) -> None:
        self.url: str = url

    def check_url(self) -> str:
        try:
            ModifiedUrl: str = self.url.strip("http://").strip("https://").split(":")[0]
        except Exception: 
            ModifiedUrl: str = self.url.strip("http://").strip("https://")
            
        if ModifiedUrl in config.BLOCKED_SITES:
            print(f"[! BLOCKED !] The url : {self.url} Has Been Blocked By The Python Proxy.")
            return ""
        
        else: 
            return self.url
