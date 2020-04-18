from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlretrieve, urlopen as uReq  # Web client
import datetime
import os
from selenium import webdriver

import shutil


def saveImages(car_id, car_soup):
    # create specific folder
    if os.path.isdir(car_id):
        shutil.rmtree(car_id)
    os.mkdir(car_id)
    os.chdir(car_id)

    # image processing...
    images = car_soup.findAll('div', {'class': 'thumbnail-image'})
    for ind, image in enumerate(images):
        img_src = image.find('img')['src']
        urlretrieve(img_src, "{}.jpg".format(ind))

    # end processing
    os.chdir('..')


def saveCSV(car_url, car_data_dict):
    # FEATURE: car ID
    car_id = car_url.split('/')[5]
    car_data_dict['Id'] = car_id

    # FEATURE: car Price
    gel_price, usd_price = car_soup.findAll('span', {'class': 'car-price'})
    usd_price = usd_price.text
    if usd_price != 'Price negotiable':
        usd_price = usd_price.split()[0]
        usd_price = usd_price.replace(',', '')
        car_data_dict['Price'] = usd_price
    else:
        car_data_dict['Price'] = 'Price negotiable'

    # FEATURE: car customs
    custom_soup = car_soup.find('div', {'class': 'levy'})
    if custom_soup:
        custom = custom_soup.findAll('span')[1].findAll('span')[1].text
        custom = custom.split()[0]
        custom = custom.replace(',', '')
        car_data_dict['Customs'] = custom
    else:
        car_data_dict['Customs'] = ''

    # FEATURE: Data from <tr>-s
    car_data_table = car_soup.findAll('tr')
    for data in car_data_table:
        th1, th2 = data.findAll('th')

        # th1
        th1_divs = th1.findAll('div')
        if len(th1_divs) == 2:
            th1_key, th1_value = map(
                lambda x: x.text.strip(), th1_divs)
            if th1_key in car_data_dict:
                car_data_dict[th1_key] = th1_value

        # th2
        th2_divs = th2.findAll('div')
        if len(th2_divs) == 2:
            th2_key, th2_value = th2_divs
            th2_key = th2_key.text.strip()
            if 'class' in th2_value.i.attrs and 'fa-check' in th2_value.i['class']:
                res = '1'
            else:
                res = '0'

            th2_value = res
            if th2_key in car_data_dict:
                car_data_dict[th2_key] = th2_value


if __name__ == "__main__":
    folder = 'data0110'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    os.chdir(folder)
    data_headers = ['Id', 'Manufacturer', 'Model', 'Category', 'Mileage', 'Gear box type', 'Doors',
                    'Wheel', 'Color', 'Interior color', 'VIN', 'Leather interior', 'Price', 'Customs']

    # write headers
    f = open('cars.csv', "w", encoding='utf-8')

    data_headers_str = ','.join(data_headers) + '\n'
    f.write(data_headers_str)

    URL = "https://www.myauto.ge/en/s/00/0/00/00/00/00/00/cars?stype=0&currency_id=3&det_search=0&ord=7&category_id=m0&keyword=&page={}"
    page = 1
    hasNext = True
    start_time = datetime.datetime.now()
    driver = webdriver.Chrome()
    while hasNext:
        print("Extracting page {}... Elapsed Time {}".format(
            page, datetime.datetime.now() - start_time))
        # get/parse current url
        page_url = URL.format(page)
        uClient = uReq(page_url)
        page_soup = soup(uClient.read(), "html.parser")
        uClient.close()

        # check if last page
        if page_soup.find('i', {'class': 'fa fa-forward'}) == None:
            hasNext = True
        page += 1
        cars = page_soup.findAll("h4", {"itemprop": "name"})
        # iterate over each car
        cur_data_str = ''
        for car_page in cars:
            # go to each car's url
            car_url = car_page.a['href']
            driver.get(car_url)
            car_soup = soup(driver.page_source, "html.parser")

            # DATA
            car_data_dict = {header: '' for header in data_headers}

            saveCSV(car_url, car_data_dict)
            saveImages(car_data_dict['Id'], car_soup)

            # create string
            cur_data_str += ','.join([car_data_dict[x].replace('\n', ' ')
                                      for x in data_headers]) + '\n'
        f.write(cur_data_str)

        driver.close()
        exit()
        f.close()  # Close the file
