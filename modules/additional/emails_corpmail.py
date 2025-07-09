from bs4 import BeautifulSoup
from typing import List
import requests
import re

class CorpEmailExtractor:
    def __init__(self, html_content: str):
        """
        Initialize the extractor with HTML content.
        """
        self.soup = BeautifulSoup(html_content, "html.parser")

    def find_corp_emails(self, url:str) -> List[str]:
        """
        Find all email addresses linked with @domain in the HTML.
        """
        print('Extracting emails (method 3)')
        emails = set()
            
        domain = re.search(r"https?://([^/]+)", url).group(1)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        for email in re.findall(email_pattern, self.soup.get_text()):
            # Фильтрация email-адресов по домену, если это нужно
            if domain in email:
                emails.add(email)

        if len(emails) == 1:
            return list(set(emails))
        return list(set(emails))


# Отдельный тест класса
if __name__ == "__main__":
    print("Starting tests for CorpEmailExtractor...\n")

    try:
        url = 'http://www.tolevskypartners.com.au/'

        response = requests.get(url)

        extractor = CorpEmailExtractor(response.text)
        emails = extractor.find_corp_emails(url)
        
        print(emails)

        print("\nAll tests completed.")

    except Exception as e:
        print(e)