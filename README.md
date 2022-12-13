# glassdoor-py

Python utility for fetching company reviews using the Glassdoor API and BeautifulSoup.

## Requirements:

1. Python 2.7.X
2. beautifulsoup4
3. requests

## Getting started

1. Clone this repo:

    ```
    $ git clone https://github.com/whittlbc/glassdoor-py
    ```

2. Make sure virtualenv is installed:

    ```
    $ which virtualenv
    ```
  
    If it's not installed, just pip install it:

    ```
    $ pip install virtualenv
    ```

3. Make sure the following environment variables are available (Personally, I just use a `.env` file and autoenv):

    `GLASSDOOR_PARTNER_ID`<br>
    `GLASSDOOR_PARTNER_KEY`

    You can get these by requesting access to Glassdoor's API (https://www.glassdoor.com/developer/index.htm)

4. Inside the project's root folder set up a new virtual environment and install requirements:

    ```
    $ virtualenv venv
    ```
    ```
    $ source venv/bin/activate
    ```
    ```
    $ pip install -r requirements.txt
    ```

## Fetching Company Reviews

1. Create a `data` directory inside the root of the project (`$ mkdir data`) and inside it, place a JSON file called `company_names.json` that contains a JSON array of company names you wish to get Glassdoor reviews for.

    Example `data/company_names.json`:
  
    ```
    [
      "Alteryx",
      "Altice USA",
      "Carvana",
      "Elevate Credit",
      ...
    ]
    ```
  
2. Use the Glassdoor API and BeautifulSoup to scrape the reviews for each company in `company_names.json`:

    ```
    $ python scrape_reviews.py
    ```

    This should output company reviews data to `data/company_reviews.json` with the following data structure:

      ```
      {
        "A.S.V.": [
          {
            "cons": "Working outside.Paying for uniforms.Sometimes shifts are understaffed.", 
            "pros": "Flexible schedule. Good management. Great money for the level of the job. Training.", 
            "stars": "4", 
            "summary": "Great company!"
          }
          ...
        ]
        ...
      }
      ```
    
    Whenever you wish to fetch reviews for other companies, simply update `company_names.json` and re-run `scrape_reviews.py`.

## License

MIT. Go crazy.
