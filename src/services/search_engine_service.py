import os

from playwright.sync_api import sync_playwright
from duckduckgo_search import DDGS


class SearchEngineService:
    __CUSTOMER_SEARCH_TEMPLATES = ["linkedin", "facebook", "twitter", "interview", "news"]
    __COMPANY_SEARCH_TEMPLATES = ["linkedin", "site", "financial reports", "news", "vacancies"]

    def __init__(self):
        self.search_engine = DDGS()

    def get_customer_search_results(self, customer_name: str, company_name: str) -> list[dict]:
        search_results = []

        for template in self.__CUSTOMER_SEARCH_TEMPLATES:
            search_results.extend(
                self.search_engine.text(keywords=(customer_name + " " + company_name + " " + template), max_results=10)
            )

        return search_results

    def get_company_search_results(self, company_name: str) -> list[dict]:
        search_results = []

        for template in self.__COMPANY_SEARCH_TEMPLATES:
            search_results.extend(
                self.search_engine.text(keywords=(company_name + " " + template), max_results=10)
            )

        return search_results

    def get_page_content(self, url: str) -> dict[str, str] | None:
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_timeout(5000)
                return {"url": url, "content": page.evaluate("""
                    () => {
                        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                        let visibleText = '';
                        let node;
                        while (node = walker.nextNode()) {
                            if (node.parentElement && getComputedStyle(node.parentElement).display !== 'none' &&
                                getComputedStyle(node.parentElement).visibility !== 'hidden') {
                                visibleText += node.nodeValue.trim() + '\\n';
                            }
                        }
                        return visibleText.trim();
                    }
                """).replace("\n", "")}
            except Exception as e:
                print(e)
            finally:
                browser.close()
