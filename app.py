from utils.webdriver_handler import dynamic_page
from utils.parser_handler import init_parser
from utils.setup import setSelenium
import os
from math import inf


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def crawl_casas_bahia():
    driver = setSelenium(False)
    src_code = dynamic_page(driver, "https://www.casasbahia.com.br/c/?filtro=d41033&ordenacao=precoCrescente&icid=197947_hp_stc_c7_ps1_b0_pb2&origem=co&faixapreco=899to1413")
    driver.quit()

    print('> raspando preços...')
    soap = init_parser(src_code)

    tvs = soap.find('div', class_="styles__Wrapper-crf3j2-0 hMJXmq").find('div')
    print(f'{len(tvs)} tvs encontradas...')

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

        current_tv_item = f"Título: {title}\n\nPreço: {price}\n\nLink: {link}"

        if price != 'Não disponível...':
            raw_price = price.split(' ')[2]
            sanitized_price = raw_price.split(',')[0]

            # format price to validade
            if lowest_tv > float(sanitized_price):
                lowest_tv = float(sanitized_price)
                current_tv = current_tv_item

    print(f"TV com menor preço: {current_tv}")


def main():
    """
    Insert yout code here
    """

    print('> Iniciando crawler...')
    crawl_casas_bahia()    

if __name__ == "__main__":
    main()
