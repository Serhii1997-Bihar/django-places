import re
from typing import List

import requests

from .email_domains import top_email_domains

class EmailExtractor:
    def __init__(self, domains: List[str]):
        self.domains = domains
        self.domain_pattern = "|".join(re.escape(domain) for domain in domains)
        self.email_pattern = rf"[a-zA-Z0-9._%+-]+(?:{self.domain_pattern})"

    def extract(self, text: str) -> List[str]:
        print('Extracting emails (method 1)')
        emails = re.findall(self.email_pattern, text)
        
        if len(emails) == 1:
            return list(set(emails))
        return list(set(emails))
    

# Отдельный тест класса
if __name__ == "__main__":
    print("Starting tests for EmailExtractor...\n")

    try:
        url = 'http://www.tolevskypartners.com.au/'
       
        email_extractor = EmailExtractor(top_email_domains)
        response = requests.get(url)

        emails = email_extractor.extract(response.text)
        
        print(emails)

        print("\nAll tests completed.")

    except Exception as e:
        print(e)