from utils.webdriver_handler import dynamic_page
from utils.parser_handler import init_crawler, init_parser
from utils.setup import setSelenium
import os
from decimal import Decimal
from re import sub


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def crawl_casas_bahia():
    driver = setSelenium(False)
    src_code = dynamic_page(driver, "https://www.casasbahia.com.br/c/?filtro=d41033&ordenacao=precoCrescente&icid=197947_hp_stc_c7_ps1_b0_pb2&origem=co&faixapreco=899to1413")
    driver.quit()

    print('> raspando preços...')
    soap = init_parser(src_code)

    tvs = soap.find('div', class_="styles__Wrapper-crf3j2-0 hMJXmq").find('div')
    print(f'{len(tvs)} tvs encontradas...')

    lowest_tv = 0
    current_tv = ''

    for index, tv in enumerate(tvs):
        print(f"Verificando {index + 1} tv...")
        link = tv.find('a', class_="styles__Title-sc-1gzprri-1 kWIhVj")['href']
        title = tv.find('a', class_="styles__Title-sc-1gzprri-1 kWIhVj").get_text()
        try:
            price = tv.find('a', class_="styles__PriceWrapper-sc-1idhk7x-0 hvGsJA").get_text(separator=" ")
        
        except AttributeError:
            price = 'Não disponível...' 

        current_tv_item = f"Título: {title}\n\nPreço: {price}\n\nLink: {link}"

        sanitized_price = price.split(' ')[2]
        price_final = Decimal(sub(r'[^\d.]', '', sanitized_price))
        print(price_final)
        # format price to validade
        if price != 'Não disponível...' and lowest_tv < price_final:
            lowest_tv = price
            current_tv = current_tv_item

    print(f"Menor preço: {lowest_tv}")
    print(f"TV atual: {current_tv}")


def main():
    """
    Insert yout code here
    """

    print('> Iniciando crawler...')
    crawl_casas_bahia()    

if __name__ == "__main__":
    main()
