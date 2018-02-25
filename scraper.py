import csv

import requests
from bs4 import BeautifulSoup

class Scraper:

    def __init__(self):
        self.headers = {
            "User-Agent":
                "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        }

        self.url = 'https://www.thuiswinkel.org/bedrijven/thuiswinkel-zakelijk/leden/ledenlijst'
        self.href_list = []
        self.company_list = []
    """
    fill_href_list is een helper methode voor get_href_list
    deze methode pakt alle href's met thuiswinkel.org van hoofdpagina en stopt ze in self.href_list
    """
    def fill_href_list(self, section_list):
        for section in section_list:
            ankor_list = section.findAll('a')
            for ankor in ankor_list:
                href = ankor.get('href')
                #als eerste letters met / bedrijven beginnen pas url aan
                if href[:10] == '/bedrijven':
                    self.href_list.append('https://www.thuiswinkel.org' + href)
                #als https://www.thuiswinkel.org in url zit stop in self.hreflist
                elif 'https://www.thuiswinkel.org' in href:
                    self.href_list.append(href)

    def get_href_list(self):
        req = requests.get(self.url, self.headers)
        plain_text = req.text
        soup = BeautifulSoup(plain_text, 'html.parser')

        section_list = soup.findAll('div', {'class': 'section'})
        self.fill_href_list(section_list)
        return self.href_list

    def correct_href_list(self, href_list):
        for href in href_list:
            if '/zakelijk-kopen' in href:
                href_list.remove(href)
                href = href.replace('/zakelijk-kopen', '/thuiswinkel-zakelijk')
                href_list.append(href)

    def spider(self):
        href_list = self.get_href_list()
        corrected_list =[]
        for href in self.href_list:
            if '/zakelijk-kopen' in href:
                href_list.remove(href)
                href = href.replace('/zakelijk-kopen', '/thuiswinkel-zakelijk')
                corrected_list.append(href)

            else:
                corrected_list.append(href)

        for url in corrected_list:
            print(url)
            req = requests.get(url, self.headers)
            plain_text = req.text
            soup = BeautifulSoup(plain_text, 'html.parser')
            try:
                company_dict = {}
                company = soup.find('h5').text

                table = soup.find('table', {'class': 'table'})

                table_data_list = table.findAll('td')

                vestigings_adres_header = table_data_list[0].text
                vestigings_adres_data = table_data_list[1].text
                vestigings_adres_data = vestigings_adres_data.replace("\n", '')
                vestigings_adres_data = vestigings_adres_data.replace("\xa0", '')
                vestigings_adres_data = vestigings_adres_data.replace("\u200b", '')
                print('vestigings_adres_header: ' + vestigings_adres_header)
                print('vestigings_adres_Data: ' + vestigings_adres_data)

                vestigings_postcode_header = 'Postcode:'
                vestigings_postcode_data = table_data_list[3].text
                vestigings_postcode_data = vestigings_postcode_data.replace("\n", '')
                vestigings_postcode_data = vestigings_postcode_data.replace("\xa0", '')
                vestigings_postcode_data = vestigings_postcode_data.replace("\u200b", '')
                print('vestigings_postcode_header: ' + vestigings_postcode_header)
                print('vestigings_postcode_Data: ' + vestigings_postcode_data)

                web_adres_header = table_data_list[14].text
                web_adres_data = table_data_list[15].text
                web_adres_data = web_adres_data.replace("\n", '')
                web_adres_data = web_adres_data.replace("\xa0", '')
                web_adres_data = web_adres_data.replace("\u200b", '')
                print('web_adres_header: ' + web_adres_header)
                print('web_adres_Data: ' + web_adres_data)

                kvk_header = table_data_list[17].text
                kvk_data = table_data_list[18].text
                kvk_data = kvk_data.replace("\n", '')
                kvk_data = kvk_data.replace("\xa0", '')
                kvk_data = kvk_data.replace("\u200b", '')
                kvk_data = kvk_data.replace("\BE04", '')
                print('kvk_header: ' + kvk_header)
                print('kvk_data: ' + kvk_data)

                company_dict['company'] = company
                company_dict[vestigings_adres_header] = vestigings_adres_data
                company_dict[vestigings_postcode_header] = vestigings_postcode_data
                company_dict[web_adres_header] = web_adres_data
                company_dict[kvk_header] = kvk_data

                self.company_list.append(company_dict)
            except Exception as e:
                print(e)

    def write_to_csv(self):
        company_list = self.company_list
        print(company_list)
        with open('thuiswinkel-zakelijk.csv', 'w') as file:
            try:
                headings = (self.company_list[0].keys())
                writer = csv.DictWriter(file, headings, dialect='excel')
                writer.writeheader()
                writer.writerows(company_list)
            except Exception as e:
                print(e)
s = Scraper()
s.spider()
s.write_to_csv()

