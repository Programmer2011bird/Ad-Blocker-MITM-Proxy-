from urllib.parse import urlparse
import config
import re


class search_keywords:
    def __init__(self) -> None:
        self.suspicious_word = re.compile(
            r'\b(login|verify|secure|account|update|confirm|banking|signin|'
            r'auth|authenticate|2fa|free|giftcard|winner|lottery|prize|'
            r'paypal|appleid|microsoft|dropbox|download\.exe|setup\.exe|'
            r'installer|update-flash|bitcoin|wallet|crypto)\b',
            re.IGNORECASE
        )

        self.suspicious_embedded = re.compile(
            r'\b(scam|phish|malware|ransom|trojan|fake|fraud|spoof|deceptive)',
            re.IGNORECASE
        )

        self.ad_patterns = re.compile(
            r'\b(doubleclick|googleadservices|googlesyndication|adserver|'
            r'adsrv|ad\.doubleclick|pagead2|adwords|adnxs|outbrain|taboola|'
            r'criteo|casalemedia|exelator|adsymptotic|adform|revcontent|money)\b|'
            r'(^|\.)(ad|ads|adservice|adserver)[\./]',
            re.IGNORECASE
        )
        
        self.bad_tlds = re.compile(
            r'\.(tk|ml|ga|cf|xyz|top|work|date|download|review|surf|'
            r'click|trade|webcam|racing|accountant)$',
            re.IGNORECASE
        )
        
        self.typosquatting = re.compile(
            r'(go0gle|g00gle|faceb00k|twitt3r|micros0ft|'
            r'amaz0n|app1e|micr0soft|paypa1|gmail\.cm)',
            re.IGNORECASE
        )
        
        self.suspicious_chars = re.compile(
            r'[%][0-9a-f]{2}|'      # URL encoding
            r'[@].*[.](com|org|net)|'  # @ in domain (rare)
            r'[-]{3,}',              # multiple hyphens
            re.IGNORECASE
        )

    def check(self, url):
        blocked_url = []
        if self.suspicious_word.search(url): print(f"{url}: suspicious words"); blocked_url.append(url)
        if self.suspicious_embedded.search(url): print(f"{url}: suspicious words"); blocked_url.append(url)
        if self.ad_patterns.search(url): print(f"{url}: suspicious words"); blocked_url.append(url)
        if self.bad_tlds.search(url): print(f"{url}: bad tlds"); blocked_url.append(url)
        if self.typosquatting.search(url): print(f"{url}: suspicious words"); blocked_url.append(url)
        if self.suspicious_chars.search(url): print(f"{url}: suspicious words"); blocked_url.append(url)

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]
            
            if self.bad_tlds.search(domain):
                print(f"{url}: bad_tld")
                blocked_url.append(url)
            
            if self.typosquatting.search(domain):
                print(f"{url}: typosquatting")
                blocked_url.append(url)

            for label in domain.split('.'):
                if self.suspicious_embedded.search(label):
                    print(f"{url}: suspicious_domain_label")
                    blocked_url.append(url)
                    break
                    
        except Exception:
            pass

        return blocked_url

class Blocker:
    def __init__(self, url: str) -> None:
        self.url: str = url

    def check_url(self) -> str:
        try:
            ModifiedUrl: str = self.url.strip("http://").strip("https://").split(":")[0]
        except Exception: 
            ModifiedUrl: str = self.url.strip("http://").strip("https://")

        A = search_keywords()
        Blocked_URLS = A.check(ModifiedUrl)
            
        if ModifiedUrl in config.BLOCKED_SITES or Blocked_URLS:
            print(f"[! BLOCKED !] The url : {self.url} Has Been Blocked By The Python Proxy.")
            return ""
        
        else: 
            return self.url
