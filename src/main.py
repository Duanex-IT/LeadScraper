import argparse

from dotenv import load_dotenv

from src.services.ai_service import AIService
from src.services.doc_service import DocService

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--customer", type=str, help="Customer name", required=True)
parser.add_argument("--company", type=str, help="Company name", required=True)

if __name__ == "__main__":
    args = parser.parse_args()

    ai_service = AIService(customer_name=args.customer, company_name=args.company)
    result = ai_service.get_info()

    doc_service = DocService(customer_info=result[0], company_info=result[1], related_links=result[2])
    doc_service.create_doc()
