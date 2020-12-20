from selenium import webdriver
from bs4 import BeautifulSoup as bs4
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from time import sleep
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
import os

website = """
#########################################
#           WEBSITE: Buono Mobilita 2020       #
######################################### 
"""
print(website);
start_time = datetime.now();
print('Scrap starting time : {}' .format(start_time.time()));

store_names, store_address, website, email, phone = [],[],[],[],[] 

url = "https://www.buonomobilita.it/mobilita2020/#/doveUsareBuoni"

# dict = {'city' : {pages to scrap}}
dict = {}

file = open("cities.txt",'r')
lines = file.readlines()
count = 0
for line in lines: 
    data = line.split(',')
    dict[data[0]]=int(data[1])

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('window-size=1980,1080')
options.add_argument('--start-maximized')
driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
driver.get(url)
action = ActionChains(driver)
sleep(2)

print('\n')
print(dict)
    
def fillcity(city):
    cityElement = driver.find_element_by_xpath("//input[@placeholder='Provincia']")
    action.move_to_element(cityElement).perform()
    sleep(2)
    cityElement.clear()
    cityElement.send_keys(city)
    cityElement.send_keys(Keys.ENTER)

def scrap():
    for city in dict:
        fillcity(city)
        sleep(2)

        inputPages = dict[city]
        storesText = driver.find_element_by_xpath("//div[@class='col-12 list_shop']").text
        
        # validate city name
        if 'Negozi fisici e online' in storesText:
            totalStores = storesText.replace('Negozi fisici e online','').replace(' ','')
            totalPages = int(totalStores)//10
            print('\nCity '+ city +' has total '+ totalStores + ' stores.')
            
            # validate user input for number of scraping pages
            if totalPages >= inputPages:
                
                print('--- For city {}, scraping for total {} pages started ------'.format(city,inputPages))
                for page_num in range(1,inputPages+1):
                    
                    page = driver.page_source
                    soup = bs4(page, 'html.parser')
                    dom = etree.HTML(str(soup))
                    
                    for i in range(1,11):
                        name = dom.xpath('((//div[@class="col-12 list_card"])['+str(i)+']//div[@class="col-12 list_shop_data"])[1]/text()')
                        store_names.append(listostring(name))

                        address = dom.xpath('((//div[@class="col-12 list_card"])['+str(i)+']//div[@class="col-12 list_shop_data"])[2]//span/text()') 
                        store_address.append(listostring(address))

                        web = dom.xpath('((//div[@class="col-12 list_card"])['+str(i)+']//div[@class="col-12 list_shop_data"])[3]//span//a/text()')
                        website.append(listostring(web))

                        mail = dom.xpath('((//div[@class="col-12 list_card"])['+str(i)+']//div[@class="col-4 align_div list_shop_icon visual_indent_mobile"])[1]/text()')
                        email.append(listostring(mail))

                        contact = dom.xpath('((//div[@class="col-12 list_card"])['+str(i)+']//div[@class="col-4 align_div list_shop_icon visual_indent_mobile"])[2]/text()')
                        phone.append(listostring(contact))

                    print('------ page {} done ---------'.format(page_num))
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    driver.find_element_by_css_selector('.fa-angle-right').click()
                    sleep(2)

                print('--- For city {}, scraping for total {} pages completed ------'.format(city,inputPages))
                showOutput(city)
                for list in [store_names, store_address, website, email, phone]:
                    list.clear()

            else:
                try:
                    input = int(inputPages)
                except ValueError:
                    print("Number of pages is not an integer")
                print('For this city user input is: '+ str(inputPages) +' pages. Maximum pages that can be scraped is ' + str(totalPages))
                continue

        elif 'Nessun punto vendita soddisfa i criteri di ricerca' in storesText:
            print('\nCity '+ city +' does not exist. Please fill a valid city name')
            continue
    
    dict.clear()
    driver.quit()
    
def showOutput(city):
    data={'STORE NAME':store_names,'STORE ADDRESS':store_address,'WEBSITE':website,'EMAIL':email,'PHONE':phone}
    df=pd.DataFrame(data=data)
    df.index = df.index + 1

    # printing single excel for each city
    excel_name = city + '_{}.xlsx' .format(datetime.now().date())
    csv_name = city + '_{}.csv' .format(datetime.now().date())
    df.to_excel(os.path.join(os.path.curdir, 'ExcelOutput/' + excel_name))
    df.to_csv(os.path.join(os.path.curdir, 'CSVOutput/' + csv_name))

def listostring(list):
    string = ""
    if(len(list)==0):
        list.append('NA')
    return (string.join(list).replace(' ','')) 

scrap()

