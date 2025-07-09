from typing import List
import requests
from html.parser import HTMLParser

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Cookie": "LOGIN_INFO=AFmmF2swRQIhAPnQlOhsYgSuM9_TY4-RUbxy_zHG1VOocnEcqo9QMYpuAiBmr53RVz9SYLctC6-oeXc330mAxSNzi5Z9SuTmoOjV4Q:QUQ3MjNmei0yaXJFbkNUN0dBUGNDNklSTFVGVENSc1dyMXpDTlY3Z2F0bFE3blB4MkJXREU0azVOU18xRzhZZzB4eldXR2F1NlpwN3BrQVdFZ2xuNEQySVlhNzJRanRGWWlqTnNRZGIzUWl5NDNhdEZKYW5ZMGNMR1lPQm1IQmROUGRjSEZaalhTMFdla1FBN1prdTA1b2FScjJqRmg4NTVR; YSC=eWd-YdLgE9s; VISITOR_INFO1_LIVE=137Bgu1Nsmg; VISITOR_PRIVACY_METADATA=CgJVQRIEGgAgbg%3D%3D; SID=g.a000qwjCosVaMauBZgzsgXczPBb_58d4JZmJ6Ib352KZPzzPCGaI7eLTjO3zfMu4CUm4wcmK0gACgYKAYYSARYSFQHGX2MiOeBYCS7wmA8KzyJJGUMT2BoVAUF8yKppiO-8yabDG5DociAoCmCx0076; __Secure-1PSID=g.a000qwjCosVaMauBZgzsgXczPBb_58d4JZmJ6Ib352KZPzzPCGaIg844XdG0CgUK0ck0770B_wACgYKASsSARYSFQHGX2MikIu991DwupRKxawnPrt9jhoVAUF8yKqKwRbxNmNN636LyLcsyLu80076; __Secure-3PSID=g.a000qwjCosVaMauBZgzsgXczPBb_58d4JZmJ6Ib352KZPzzPCGaIgt4-sk2kcFkIPCpNtXJuXAACgYKAcASARYSFQHGX2MiROBjovcPVXp0ZM9IQp8brhoVAUF8yKrcc0hy0FeNSVqCsSct4-yj0076; HSID=AjaXUdRNRo-4momGA; SSID=A72eoUdyYNuMDYltW; APISID=L6XgLLiBTnF5cg_s/ABtw7rUCnNMuM_b-V; SAPISID=B3AAS8hIuCZcmrOg/AQP1YWhi7-nK_wd2Z; __Secure-1PAPISID=B3AAS8hIuCZcmrOg/AQP1YWhi7-nK_wd2Z; __Secure-3PAPISID=B3AAS8hIuCZcmrOg/AQP1YWhi7-nK_wd2Z; wide=1; __Secure-1PSIDTS=sidts-CjEBQT4rXxLkxwwBizroa4t09Ms8WrmYTR9qtbrxdvuTEvaovJmhL7e7MGVWpZUYN8xbEAA; __Secure-3PSIDTS=sidts-CjEBQT4rXxLkxwwBizroa4t09Ms8WrmYTR9qtbrxdvuTEvaovJmhL7e7MGVWpZUYN8xbEAA; PREF=f6=40000000&f7=4100&tz=Europe.Chisinau&f4=4000000&f5=30000&repeat=ONE&volume=50&autoplay=true&hl=en; SIDCC=AKEyXzWbb5BnxiWB3anbFO4eY7fTjkQXh1fQIpjzSTtT7RoOejZbl2-rb_R7_a1TdOhpk6m-5EU; __Secure-1PSIDCC=AKEyXzU5JimytDIkdAML9lg-K9rB0ejOdPGIH6aCLOeQILM8CsMO72g9qzKMKAmHPnrh714sDg; __Secure-3PSIDCC=AKEyXzVeFeM_ryQpyMORn-SISgLPfiAj645K0vmJYIH2rghTnEZlZ2_95MDxIfEsNvohGIhDMg; ST-l3hjtt=session_logininfo=AFmmF2swRQIhAPnQlOhsYgSuM9_TY4-RUbxy_zHG1VOocnEcqo9QMYpuAiBmr53RVz9SYLctC6-oeXc330mAxSNzi5Z9SuTmoOjV4Q%3AQUQ3MjNmei0yaXJFbkNUN0dBUGNDNklSTFVGVENSc1dyMXpDTlY3Z2F0bFE3blB4MkJXREU0azVOU18xRzhZZzB4eldXR2F1NlpwN3BrQVdFZ2xuNEQySVlhNzJRanRGWWlqTnNRZGIzUWl5NDNhdEZKYW5ZMGNMR1lPQm1IQmROUGRjSEZaalhTMFdla1FBN1prdTA1b2FScjJqRmg4NTVR"
}

class MailtoEmailExtractor(HTMLParser):
    def __init__(self, html_content: str):
        """
        Initialize the extractor with HTML content.
        """
        super().__init__()
        self.mailto_links = []
        self.feed(html_content)

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """
        Handle start tags and collect mailto links.
        """
        if tag == "a":
            for attr_name, attr_value in attrs:
                if attr_name == "href" and attr_value and attr_value.startswith("mailto:"):
                    self.mailto_links.append(attr_value)

    def find_emails(self) -> List[str]:
        """
        Extract email addresses from collected mailto links.
        """
        print("Extracting emails (method 2)")
        emails = set()
        for href in self.mailto_links:
            email = href[7:]  # Remove "mailto:" prefix
            email = email.split("?")[0]  # Remove query parameters if any
            if email:
                emails.add(email)
        return list(emails)

# Отдельный тест класса
if __name__ == "__main__":
    print("Starting tests for MailtoEmailExtractor...\n")

    try:
        url = 'http://www.tolevskypartners.com.au/'

        response = requests.get(url, headers=headers)

        extractor = MailtoEmailExtractor(response.text)
        emails = extractor.find_emails()

        print(emails)

        print("\nAll tests completed.")

    except Exception as e:
        print(e)
