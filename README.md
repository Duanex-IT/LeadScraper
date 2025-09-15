# LeadScraper
## Installation
1. Clone the project into your working directory:
   * HTTPS
   ```sh
   git clone https://github.com/Duanex-IT/LeadScraper.git
   ```
   * SSH
   ```sh
   git clone git@github.com:Duanex-IT/LeadScraper.git
   ```
2. Сreate an ```.env``` file in ```src/``` with these params:
   ```
   OPENAI_API_KEY=<key>
   ```
3. Navigate to the project's root folder and create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   * For Windows:
   ```
   .\venv\Scripts\activate
   ```
   * For Unix:
   ```
   source venv/bin/activate
   ```
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Run:
   ```
   playwright install
   ```

## Usage
```
python -m src.main --customer "<CUSTOMER_NAME>" --company "<COMPANY_NAME>"
```
The ```.docx``` file will be saved in the ```output``` folder.
