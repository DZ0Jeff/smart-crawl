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

    print('> Iniciando...', end="\r", flush=True)
    driver = setSelenium(False)
    src_code = dynamic_page(driver, 'https://www.casasbahia.com.br/c/?filtro=d41033&ordenacao=precoCrescente&icid=197947_hp_stc_c7_ps1_b0_pb2&origem=co&faixapreco=899to1413')
    driver.quit()

    print("> Raspando elementos...", end="\r", flush=True)
    soap = init_parser(src_code)

    tvs = soap.find('div', class_="Row-sc-1s8ruxj-0 iWSNLk")
    print(tvs.prettify())


if __name__ == "__main__":
    main()
