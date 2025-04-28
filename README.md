This is a simple web scraper that fetches content from https://iga.in.gov/legislative/2025/bills and outputs information in json format like below.

{
  "title": "Senate Bill 1 • Water matters.",
  "sponsors": ["Sen. Eric Koch", "Sen. Chris Garten", "Sen. Susan Glick"],
  "digest": "Prohibits...",
  "actions": "02/25/2025 Senate Signed by Governor 02/20/2025 House ...",
  "source": "https://iga.in.gov/legislative/2025/bills/senate/1/details"
}

It leverages Selenium, beautifulsoup to scrape from dynamically loaded website and able to automatically click "view more" button to fetch data underneath if exists on the page.
To run automation across the site, one way is to loop this program over the url https://iga.in.gov/legislative/2025/bills/senate/n/details 
