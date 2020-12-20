# Bonus-Mobilita-Web-Scraper
This project scrap the Bonus Mobility([Buono Mobilita 2020](https://www.buonomobilita.it/mobilita2020/#/doveUsareBuoni)) website to have easy access to the details of cycle stores in different Italian cities, which accepts the bonus mobility voucher.

**How to Run** 
- Clone the repository and cd to root folder
- pip3 install -r requirements.txt
- Add a new city and number of pages to scrap in [inputCities.txt](https://github.com/robinch93/Bonus-Mobilita-Web-Scraper/blob/master/inputCities.txt) file in example format. Refer [this](https://en.wikipedia.org/wiki/List_of_cities_in_Italy) link to enter valid city names. &nbsp;
  Example: MILANO,4 
- python3 scrap.py
- Find Results in [Excel Output](https://github.com/robinch93/Bonus-Mobilita-Web-Scraper/tree/master/ExcelOutput) and [CSV Output](https://github.com/robinch93/Bonus-Mobilita-Web-Scraper/tree/master/CSVOutput) folder in excel and csv format respectively.
