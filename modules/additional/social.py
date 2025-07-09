import requests
from bs4 import BeautifulSoup
from typing import Dict


class SocialLinksExtractor:
    def __init__(self, headers: Dict[str, str]):
        """
        Initialize the SocialLinksExtractor with headers for requests.
        """
        self.headers = headers

    def extract_links(self, url: str) -> Dict[str, set]:
        """
        Extract social media links from the provided URL.
        """
        print(f'Extracting social links from {url}')
        response = self._fetch_page(url)
        social_links = {
            "facebook": self._extract_facebook_links(response),
            "instagram": self._extract_instagram_links(response),
            "linkedin": self._extract_linkedin_links(response),
            "youtube": self._extract_youtube_links(response),
            "twitter": self._extract_x_links(response),
        }
        return social_links

    def _fetch_page(self, url: str) -> str:
        """
        Fetch the page content using requests and the provided headers.
        """
        print(f"Fetching {url} with headers")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url} with status code {response.status_code}")
            return ""

    def _extract_links_by_pattern(self, soup: BeautifulSoup, pattern: str) -> set:
        """
        Generic method to extract links based on a pattern.
        """
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if pattern in href:
                links.add(href)
        return links if links else None

    def _extract_facebook_links(self, page_content: str) -> set:
        """
        Extract Facebook links from the page content.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        return self._extract_links_by_pattern(soup, 'facebook.com')

    def _extract_instagram_links(self, page_content: str) -> set:
        """
        Extract Instagram links from the page content.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        return self._extract_links_by_pattern(soup, 'instagram.com')

    def _extract_linkedin_links(self, page_content: str) -> set:
        """
        Extract LinkedIn links from the page content.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        return self._extract_links_by_pattern(soup, 'linkedin.com')

    def _extract_youtube_links(self, page_content: str) -> set:
        """
        Extract YouTube links from the page content.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        return self._extract_links_by_pattern(soup, 'youtube.com')

    def _extract_x_links(self, page_content: str) -> set:
        """
        Extract Twitter/X links from the page content.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        return self._extract_links_by_pattern(soup, 'twitter.com') or \
               self._extract_links_by_pattern(soup, 'x.com')


# Отдельный тест класса
if __name__ == "__main__":
    print("Starting tests for SocialLinksExtractor...\n")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Cookie": "LOGIN_INFO=AFmmF2swRQIhAPnQlOhsYgSuM9_TY4-RUbxy_zHG1VOocnEcqo9QMYpuAiBmr53RVz9SYLctC6-oeXc330mAxSNzi5Z9SuTmoOjV4Q:QUQ3MjNmei0yaXJFbkNUN0dBUGNDNklSTFVGVENSc1dyMXpDTlY3Z2F0bFE3blB4MkJXREU0azVOU18xRzhZZzB4eldXR2F1NlpwN3BrQVdFZ2xuNEQySVlhNzJRanRGWWlqTnNRZGIzUWl5NDNhdEZKYW5ZMGNMR1lPQm1IQmROUGRjSEZaalhTMFdla1FBN1prdTA1b2FScjJqRmg4NTVR; YSC=eWd-YdLgE9s; VISITOR_INFO1_LIVE=137Bgu1Nsmg; VISITOR_PRIVACY_METADATA=CgJVQRIEGgAgbg%3D%3D; SID=g.a000qwjCosVaMauBZgzsgXczPBb_58d4JZmJ6Ib352KZPzzPCGaI7eLTjO3zfMu4CUm4wcmK0gACgYKAYYSARYSFQHGX2MiOeBYCS7wmA8KzyJJGUMT2BoVAUF8yKppiO-8yabDG5DociAoCmCx0076"
        }

        scraper = SocialLinksExtractor(headers)

        url = 'https://www.alexanderbright.com.au/'
        social = scraper.extract_links(url)

        print(social)

        print("\nAll tests completed.")

    except Exception as e:
        print(e)
