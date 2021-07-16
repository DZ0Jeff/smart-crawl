from time import sleep
from utils.webdriver_handler import dynamic_page
from utils.parser_handler import init_parser
from utils.setup import setSelenium
from utils.telegram import TelegramBot
import os
from math import inf
import schedule
from selenium.common.exceptions import NoSuchElementException



ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def crawl_casas_bahia(telegram):
    driver = setSelenium(False)
    src_code = dynamic_page(driver, "https://www.casasbahia.com.br/c/?filtro=d41033&ordenacao=precoCrescente&icid=197947_hp_stc_c7_ps1_b0_pb2&origem=co&faixapreco=899to1413")
    driver.quit()

    print('> raspando preços...')
    soap = init_parser(src_code)

    tvs = soap.find('div', class_="styles__Wrapper-crf3j2-0 hMJXmq").find('div')
    print(f'> {len(tvs)} tvs encontradas...')

    # start on highets, then decreases
    lowest_tv = float(inf)
    current_tv = ''

    for index, tv in enumerate(tvs):
        print(f"Verificando {index + 1} tv...", end="\r")
        link = tv.find('a', class_="styles__Title-sc-1gzprri-1 kWIhVj")['href']
        title = tv.find('a', class_="styles__Title-sc-1gzprri-1 kWIhVj").get_text()
        try:
            price = tv.find('a', class_="styles__PriceWrapper-sc-1idhk7x-0 hvGsJA").get_text(separator=" ")
        
        except AttributeError:
            price = 'Não disponível...' 

        current_tv_item = f"Tv: {title}\n\nPreço: {price}\n\nLink: {link}"

        if price != 'Não disponível...':
            raw_price = price.split(' ')[2]
            sanitized_price = raw_price.split(',')[0]

            # format price to validade
            if lowest_tv > float(sanitized_price):
                lowest_tv = float(sanitized_price)
                current_tv = current_tv_item

    print(f"TV com menor preço: {current_tv}")
    telegram.send_message(current_tv)


def crawl_magalu(telegram):
    """
    Crawl magazine luiza tvs prices

    telegram: telegram client (optional)
    """
    def convert_price(price):

        final_price = price.split('R$')[-1]
        final_price = final_price.strip().replace(',','').replace('.','')
        return int(final_price)


    url = "https://www.magazineluiza.com.br/smart-tv/tv-e-video/s/et/elit?sort=type%3Aprice%2Corientation%3Aasc"
    driver = setSelenium(False)
    try:
        driver.get(url)
        driver.implicitly_wait(10)

        lowest_tv = float(inf)
        current_msg = ''
        container = driver.find_element_by_xpath('//*[@id="showcase"]/ul[1]')
        for index, item in enumerate(container.find_elements_by_tag_name("a")):
            print(f"Extraindo {index + 1} produto", end="\r")

            tv = item.find_element_by_tag_name('h3').text
            link = item.get_attribute('href')

            test_tv = tv.lower()
            if test_tv.startswith('smart tv'):
            # change xpath to get data-css
                try:
                    price = item.find_element_by_xpath(f'//*[@id="showcase"]/ul[1]/a[{index + 1}]/div[3]/div[2]/div[2]/span[1]').text

                except NoSuchElementException:
                    try:
                        price = item.find_element_by_xpath(f'//*[@id="showcase"]/ul[1]/a[{index + 1}]/div[3]/div[2]/div[2]').text

                    except Exception:
                        price = "Não disponível..."

                msg = f"\nTv: {tv}\n\nPreço: {price}\n\nLink: {link}"
                            
                if price != "Não disponível...":
                    format_price = convert_price(price)
                    
                    if lowest_tv > format_price:
                        lowest_tv = format_price
                        current_msg = msg

        print(lowest_tv)
        print(current_msg)
        telegram.send_message(current_msg)

    except Exception:
        driver.quit()
        raise
    
    except KeyboardInterrupt:
        driver.quit()
        raise

    driver.quit()

def main():
    """
    Insert yout code here
    """
    print('> Iniciando Smart TV...')
    telegram = TelegramBot(ROOT_DIR)
    print('> iniciando Casas Bahia...')
    crawl_casas_bahia(telegram)
    print('> Iniciando Magalu...')    
    crawl_magalu(telegram)
    print('> Extração Finalizada!')


if __name__ == "__main__":
    main()
    schedule.every().day.at("12:00").do(main)
   
    while True:
        print('Esperando...', end="\r")
        schedule.run_pending()
        sleep(1)
