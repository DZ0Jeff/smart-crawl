from utils.webdriver_handler import dynamic_page
from utils.setup import setSelenium
from utils.parser_handler import init_crawler, init_parser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    """
    Insert yout code here
    """
    pass

    print('> Iniciando crawler...')
    soap = init_crawler('https://www.casasbahia.com.br/c/?filtro=d41033&ordenacao=precoCrescente&icid=197947_hp_stc_c7_ps1_b0_pb2&origem=co&faixapreco=899to1413')

    tvs = soap.find('div', class_="styles__Wrapper-crf3j2-0 hMJXmq").find('div')
    for tv in tvs:
        print(tv.text)


if __name__ == "__main__":
    main()
