from selenium import webdriver
from bs4 import BeautifulSoup as bs4
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from datetime import datetime
from time import sleep
from pathlib import Path
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
import os
import streamlit as st
from geosky import geo_plug
from translate import Translator
import json

website = """
#########################################
#           WEBSITE: Buono Mobilita 2020       #
######################################### 
"""
print(website);
# start_time = datetime.now();
# print('Scrap starting time : {}' .format(start_time.time()));

store_names, store_address, website, email, phone = [],[],[],[],[] 

url = "https://www.buonomobilita.it/mobilita2020/#/doveUsareBuoni"

# dict = {'city' : {pages to scrap}}
# dict = {}

# file = open("inputCities.txt",'r')
# lines = file.readlines()
# count = 0
# for line in lines: 
#     data = line.split(',')
#     dict[data[0]]=int(data[1])

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('window-size=1980,1080')
options.add_argument('--start-maximized')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(),options=options);
driver.get(url)
action = ActionChains(driver)
sleep(2)

print('\n')
# print(dict)
    
def fillcity(city):
    if city in english_name_cities:
        city = translateToItalian(city)
    cityElement = driver.find_element_by_xpath("//input[@placeholder='Provincia']")
    action.move_to_element(cityElement).perform()
    sleep(2)
    cityElement.clear()
    cityElement.send_keys(city.strip())
    cityElement.send_keys(Keys.ENTER)

def scrap(city,inputPages):
    # for city in dict:
        fillcity(city)
        sleep(2)

        # inputPages = dict[city]
        # inputPages = 2
        storesText = driver.find_element_by_xpath("//div[@class='col-12 list_shop']").text
        
        # validate city name
        if 'Negozi fisici e online' in storesText:
            totalStores = storesText.replace('Negozi fisici e online','').replace(' ','')
            totalStores = int(totalStores)
            if totalStores > 10 :
                totalPages = totalStores//10
            elif totalStores < 10 :
                totalPages = totalStores % 10
            print(totalPages)
            print('\nCity '+ city +' has total '+ str(totalStores) + ' stores.')
            
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
                # showOutput(city)
                # for list in [store_names, store_address, website, email, phone]:
                #     list.clear()

            else:
                try:
                    input = int(inputPages)
                except ValueError:
                    print("Number of pages is not an integer")
                st.write('For this city user input is: '+ str(inputPages) +' pages. Maximum pages that can be scraped is ' + str(totalPages))
                # continue

        elif 'Nessun punto vendita soddisfa i criteri di ricerca' in storesText:
            st.write('\n'+ city +' does not exist. Please select a valid city name')
            # continue
    
    # dict.clear()
        driver.quit()
    
def showOutput(city):
    data={'STORE NAME':store_names,'STORE ADDRESS':store_address,'WEBSITE':website,'EMAIL':email,'PHONE':phone}
    df=pd.DataFrame(data=data)
    df.index = df.index + 1

    Path("CSVOutput").mkdir(parents=True, exist_ok=True) 

    # printing single csv for each city
    csv_name = city + '_{}.csv' .format(datetime.now().date())
    df.to_csv(os.path.join(os.path.curdir, 'CSVOutput/' + csv_name))

def listostring(list):
    string = ""
    if(len(list)==0):
        list.append('NA')
    return (string.join(list)) 

def getItalianCities():
    states = geo_plug.all_Country_StateNames()
    states = json.loads(states)
    regions = []
    all_cities = []

    for i in range(len(states)):
        if list(states[i].keys())[0] == "Italy":
            regions = list(states[i].values())[0]
            
    for i in range(len(regions)):
        regionalCities = geo_plug.all_State_CityNames(regions[i])
        regionalCities = json.loads(regionalCities)
        regionalCities = list(regionalCities[0].values())[0]
        all_cities = all_cities + regionalCities

    return sorted(all_cities)

english_name_cities = ['Florence', 'Genoa', 'Rome', 'Turin', 'Venice']

def translateToItalian(text):
    translator= Translator(to_lang="it")
    translation = translator.translate(text)
    return translation

def app():
    
    header = st.beta_container()
    selection = st.beta_container()
    results = st.beta_container()
   
    with header:
        st.write("[Bonus Mobilita 2020](https://www.buonomobilita.it/mobilita2020/#/doveUsareBuoni)")

    with selection:
        with st.form('Form 1'):
            col1, col2 = st.beta_columns((2,1))
            city = col1.selectbox('city',(getItalianCities()))
            pages = col2.selectbox('pages',(1,2,3,4,5))
            submit = st.form_submit_button('Submit')

    with results:
        if submit:
            scrap(city,pages)
            data={'STORE NAME':store_names,'STORE ADDRESS':store_address,'WEBSITE':website,'EMAIL':email,'PHONE':phone}
            df=pd.DataFrame(data=data)
            # df.index = [""] * len(df)
            st.table(df)

app()


