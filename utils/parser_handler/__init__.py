import requests
from bs4 import BeautifulSoup
from requests.exceptions import InvalidSchema


def init_crawler(url):
    try:
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

        page = requests.get(url, headers=headers)

        if page.status_code != 200:
            print(f'[ERRO {page.status_code}] Site indisponivel, tente novamente mais tarde')
            return

        return BeautifulSoup(page.text, "lxml")

    except InvalidSchema:
        print('Algo deu errado!')
        return

    except ConnectionError:
        print('Não conseguiu se conectar na página!')
        return


def init_parser(html):
    return BeautifulSoup(html, "lxml")
