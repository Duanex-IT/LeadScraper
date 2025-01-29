import json

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from src.services.search_engine_service import SearchEngineService


class AIService:
    def __init__(self, customer_name: str, company_name: str):
        self.customer_name = customer_name
        self.company_name = company_name
        self.model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.3)
        self.search_engine = SearchEngineService()

    def get_info(self):
        customer_search_results = self.search_engine.get_customer_search_results(
            customer_name=self.customer_name,
            company_name=self.company_name
        )
        company_search_results = self.search_engine.get_company_search_results(
            company_name=self.company_name
        )

        relevant_customer_search_results = json.loads(
            self.__separate_relevant_customer_results(search_results=str(customer_search_results))
        )

        relevant_company_search_results = json.loads(
            self.__separate_relevant_company_results(search_results=str(company_search_results))
        )

        related_links = set(relevant_company_search_results + relevant_customer_search_results)

        fetched_customer_info = ""
        fetched_company_info = ""

        for result in relevant_customer_search_results:
            try:
                fetched_customer_info += str(self.search_engine.get_page_content(url=result))
            except Exception as e:
                print(e)

        for result in relevant_company_search_results:
            try:
                fetched_company_info += str(self.search_engine.get_page_content(url=result))
            except Exception as e:
                print(e)

        return [
            self.__summarize_customer_info(search_results=fetched_customer_info),
            self.__summarize_company_info(search_results=fetched_company_info),
            related_links
        ]

    def __separate_relevant_customer_results(self, search_results: str) -> str:
        prompt_template = """
        You are an intelligent assistant designed to analyze search engine results and filter out only the most relevant
        information based on the provided criteria.

        Here is the information you have:
        1. A customer's full name: {customer_name}
        2. A company's name: {company_name}
        3. A list of search engine results (each result includes a title, a link, and a snippet of text): {search_results}

        Your task:
        - Identify and retain only the results that are strictly relevant to the customer ({customer_name}).
        - A result is considered relevant if:
          1. It explicitly mentions or directly relates to the customer ({customer_name}).
          2. To avoid confusion with similarly named individuals, the result must also reference the company 
          ({company_name}) **OR** provide strong evidence that it refers specifically to the customer ({customer_name}),
          such as direct links to their **profile page** on a social media platform.
          3. If a result contains a link to a social media platform (e.g., LinkedIn, Facebook, Twitter, Instagram, Youtube), 
          retain **only one link**.

        - Ignore results that:
          - Mention similarly named individuals without clear evidence of relevance to the specified customer or their 
          connection to {company_name}.
          - Refer to unrelated entities, general content, indirect mentions, or irrelevant pages.

        - Deduplicate results:
          - If two or more results provide the same or similar information, retain only the most comprehensive and 
          direct link.

        Return the filtered results in the following format:
        ###
        ["href", "href", ...]
        ###
        """

        prompt = PromptTemplate(
            input_variables=["search_results", "customer_name", "company_name"],
            template=prompt_template
        ).format(search_results=search_results, customer_name=self.customer_name, company_name=self.company_name)

        return self.model.invoke(prompt).content[3:-3]

    def __separate_relevant_company_results(self, search_results: str) -> str:
        prompt_template = """
        You are an intelligent assistant designed to analyze search engine results and filter out only the most relevant
        information based on the given criteria.

        Here is the information you have:
        1. A company's name: {company_name}
        2. A list of search engine results (each result includes a title, a link, and a snippet of text): {search_results}

        Your task:
        - Identify and retain only the results that are strictly relevant to the provided company ({company_name}).
        - A result is considered relevant if:
          1. It contains clear and exact matches or strong associations to the company name ({company_name}).
          2. It provides information directly related to the company's activities, services, reputation, or any other 
          relevant details.
          3. LinkedIn profile or mentions on it.

        - Ignore results that:
          - Are ambiguous or lack clear evidence of relevance to the specified company.
          - Refer to unrelated entities, including similarly named companies or other organizations.

        - Deduplicate results:
          - If two or more results provide the same information or very similar content (even if phrased differently), 
          keep only one of them to avoid redundancy.

        Return the filtered results in the following format:
        ###
        ["href", "href", ...]
        ###
        """

        prompt = PromptTemplate(
            input_variables=["search_results", "customer_name", "company_name"],
            template=prompt_template
        ).format(search_results=search_results, company_name=self.company_name)

        return self.model.invoke(prompt).content[3:-3]

    def __summarize_customer_info(self, search_results: str) -> dict:
        prompt_template = """
        You are an intelligent assistant designed to analyze information from web pages about a company and its 
        high-ranking executive (e.g., CEO). Your goal is to extract and summarize specific details about the executive.

        Here is the information you have:
        1. **Executive's Full Name**: {customer_name}
        2. **Company Name**: {company_name}
        3. **A list of links and their associated content (title, text, etc.)**: {search_results}
        
        ### Your Task:
        Analyze the provided data to extract the following information and return it in the specified format:
        
        #### About the Executive:
        - **Full Name**: Confirmed full name of the individual.
        - **Current Position and Company**: Title (e.g., CEO) and the company they are currently associated with.
        - **Country**: The country associated with the individual (if available from the data).
        - **Social Media Links**: Direct links to the individual’s **Facebook**, **Instagram**, **Twitter**, 
        and **LinkedIn** profiles (if available). Exclude links to posts, articles, or secondary pages.
        - **Internet Mentions**: Links for any additional information that may be interesting, such as articles authored
        by the individual, mentions in the media, interviews, or other notable content.
        
        ### Guidelines:
        1. **Relevance**: Retain only information that explicitly mentions the executive ({customer_name}) of the 
        {{company_name}}.
        2. **Deduplication**: If the same information appears in multiple sources, keep only the most comprehensive and 
        reliable version.
        3. **Clarity**: Ensure that social media links are direct links to profiles (not posts or shared content).
        4. **Precision**: Ignore ambiguous or unrelated mentions of similarly named individuals or companies.
        
        ### Output Format:
        Return the extracted information in this JSON structure:
        
        "customer": {{
            "customer_name": string or null,
            "company": string or null,
            "position": string or null,
            "country": string or null,
            "social_media_links": {{
              "facebook": string or null,
              "instagram": string or null,
              "twitter": string or null,
              "linkedin": string or null
            }},
            "internet_mentions": [
              string or null,
              ...
            ]
        }}
        """
        prompt = PromptTemplate(
            input_variables=["search_results", "customer_name", "company_name"],
            template=prompt_template
        ).format(search_results=search_results, customer_name=self.customer_name, company_name=self.company_name)
        try:
            return json.loads(self.model.invoke(prompt).content[7:-3])
        except Exception as e:
            print(e)

    def __summarize_company_info(self, search_results: str) -> dict:
        prompt_template = """
        You are an intelligent assistant designed to analyze information from web pages about a company. Your goal is
        to extract and summarize specific details about the company, based on the provided data.
        
        Here is the information you have:
        1. **Company Name**: {company_name}
        2. **A list of links and their associated content (title, text, etc.)**: {search_results}
        
        ### Your Task:
        Analyze the provided data to extract the following information and return it in the specified format:
        
        - **Name**: The company's official name.
        - **Size**: Number of employees or company scale (e.g., small, medium, enterprise) if mentioned.
        - **LinkedIn**: Insert the link to the company's LinkedIn profile if it's provided.
        - **Website**: The company’s official website.
        - **Financial Information**: Revenue, funding details, or any other financial-related data.
        - **Technology and Products**: Key technologies, services, or products associated with the company.
        
        ### Guidelines:
        1. **Relevance**: Retain only information that explicitly mentions the company ({company_name}).
        2. **Deduplication**: If the same information appears in multiple sources, keep only the most comprehensive 
        and reliable version.
        3. **Clarity**: Ensure that social media links are direct links to profiles (not posts or shared content).
        4. **Precision**: Ignore ambiguous or unrelated mentions of similarly named individuals or companies.
        
        ### Output Format:
        Return the extracted information in this JSON structure:
        
        "company": {{
            "name": string or null,
            "size": string or null,
            "linkedin": string or null,
            "website": string or null,
            "financial_info": string or null,
            "tech_and_products": [
             string or null,
             ...
            ]
        }}
        """
        prompt = PromptTemplate(
            input_variables=["search_results", "company_name"],
            template=prompt_template
        ).format(search_results=search_results, company_name=self.company_name)
        try:
            return json.loads(self.model.invoke(prompt).content[7:-3])
        except Exception as e:
            print(e)
