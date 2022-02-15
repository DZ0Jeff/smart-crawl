from time import sleep
from utils.webdriver_handler import dynamic_page
from utils.parser_handler import init_crawler, init_parser
from utils.setup import setSelenium
from utils.telegram import TelegramBot
import os
from math import inf
import schedule
from selenium.common.exceptions import NoSuchElementException


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
AMAZON_LOWERS_PRICES = []
CASAS_BAHIA_LOWEST_PRICES = []
MAGALU_LOWERS_PRICES = []


def convert_price(price):
    final_price = price.split('R$')[-1]
    final_price = final_price.strip().replace(',','').replace('.','')
    return int(final_price)


def crawl_casas_bahia(telegram):
    driver = setSelenium(False)
    driver.maximize_window()
    src_code = dynamic_page(driver, "https://www.casasbahia.com.br/c/?filtro=d41033&ordenacao=precoCrescente&icid=197947_hp_stc_c7_ps1_b0_pb2&origem=co&faixapreco=899to1413")
    # driver.save_screenshot('screen.png')
    driver.quit()

    print('> raspando preços...')
    soap = init_parser(src_code)

    try:
        tvs = soap.find('div', class_="sc-881f8143-0 PQLIb").find('div', class_="sc-18eb4054-0 dPlWZd").find_all('div', class_="sc-5fec12f4-0 cxOoNz sc-881f8143-1 dCDlKd")
    
    except AttributeError as error:
        # telegram.send_message('> Erro ao pegar os preços das casas bahia!')
        print(f'> Erro ao extrair casas bahia, e:{error}')
        return

    print(f'> {len(tvs)} tvs encontradas...')

    # start on highets, then decreases
    lowest_tv = float(inf)
    current_tv = dict()

    for index, tv in enumerate(tvs):
        print(f"Verificando {index + 1} tv...", end="\r")
        link = tv.find('a', class_="sc-5b0743c3-4 fdeIsi")['href']
        title = tv.find('a', class_="sc-5b0743c3-4 fdeIsi")['title']
        
        try:
            price = tv.find('span', class_="sc-47246d2e-7 eToubG").get_text(separator=" ")
        
        except AttributeError:
            price = 'Não disponível...' 

        current_tv_item = {
            'Título': title, 
            'preço': price, 
            'link': link
        }

        # refactor in function
        if price != 'Não disponível...':
            raw_price = price.split(' ')[2]
            sanitized_price = raw_price.split(',')[0]

            # format price to validade
            if lowest_tv > float(sanitized_price):
                lowest_tv = float(sanitized_price)
                current_tv = current_tv_item

    # refactor in function
    if not current_tv['link'] in CASAS_BAHIA_LOWEST_PRICES:
        CASAS_BAHIA_LOWEST_PRICES.append(current_tv['link'])
        msg = f"Tv: {current_tv['Título']}\n\nPreço: {current_tv['preço']}\n\nLink: {current_tv['link']}"
        print(f"TV com menor preço: {msg}")
        telegram.send_message(msg)


def crawl_magalu(telegram):
    """
    Crawl magazine luiza tvs prices

    telegram: telegram client (optional)
    """

    url = "https://www.magazineluiza.com.br/smart-tv/tv-e-video/s/et/elit?sort=type%3Aprice%2Corientation%3Aasc"
    driver = setSelenium(False)
    try:
        driver.get(url)
        driver.implicitly_wait(220)

        lowest_tv = float(inf)
        current_msg = dict()
        container = driver.find_element_by_xpath('//*[@id="showcase"]/ul[1]')
        print('a extrair')
        for index, item in enumerate(container.find_elements_by_tag_name("a")):
            print(f"Extraindo {index + 1} produto", end="\r")

            tv = item.find_element_by_tag_name('h3').text
            link = item.get_attribute('href')
            print(tv)

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

                msg = {'tv': tv, 'price': price, 'link': link}
                print(msg)

                # refactor in function    
                if price != "Não disponível...":
                    format_price = convert_price(price)
                    
                    if lowest_tv > format_price:
                        lowest_tv = format_price
                        current_msg = msg

        if not 'link' in current_msg:
            print('> Erro ao extraír dados! (Sistema anti-bot ou algo mudou?)')
            driver.quit()
            return

        # refactor in function
        if current_msg['link'] in MAGALU_LOWERS_PRICES:
            MAGALU_LOWERS_PRICES.append(current_msg['link'])
            format_msg = f"\nTv: {current_msg['tv']}\n\nPreço: {current_msg['price']}\n\nLink: {current_msg['link']}"
            print(format_msg)
            telegram.send_message(format_msg)

    except Exception:
        driver.quit()
        raise
    
    except KeyboardInterrupt:
        driver.quit()
        raise

    driver.quit()


def crawl_amazon(telegram):
    """
    Crawl Amazon cheapest Smart TV

    :telegram: telegram client
    """


    def check_price(item):
        try:
            handler = item.find('a', class_="a-size-base a-link-normal a-text-normal").find('span', class_="a-offscreen")
            return handler.text

        except AttributeError:
            try:
                handler = item.find('a', class_="a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal").find('span', class_="a-price").find('span', class_="a-offscreen")
                return handler.text
            
            except Exception:
                return 'Não Disponível'


    url = "https://www.amazon.com.br/s?k=tvs+smarts&i=electronics&rh=n%3A16243822011%2Cp_n_size_browse-bin%3A17247917011&s=price-asc-rank&dc&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1626444567&rnid=16245418011&ref=sr_nr_p_n_size_browse-bin_2"

    soap = init_crawler(url)

    if soap == None or soap == False:
        return

    # save_to_html(soap)

    container = soap.find('div', class_="s-main-slot s-result-list s-search-results sg-row")

    if container == None:
        print('> Sistema anti-bot detectado, tente novamente mais tarde!')
        return

    try:
        items = container.find_all('div', class_="sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20")
        if not items:
            print('> Erro ao extraír container...')
            return

    except AttributeError:
        print('> Dados não carregados!, continuando...')
        pass 
    
    lowest_tv = float(inf)
    current_msg = {}
    for item in items:
        title = item.find('h2', class_="a-size-mini a-spacing-none a-color-base s-line-clamp-4").text
        price = check_price(item)
        link = "https://www.amazon.com.br" + item.find('a')['href']

        print("Título", title)
        print("Preço: ", price)
        print("Link:", link)

        msg = {'Título': title, 'Preço': price, 'link': link}
        # refactor in function
        if price != 'Não Disponível':
            format_price = convert_price(price)
            
            if lowest_tv > format_price:
                lowest_tv = format_price
                current_msg = msg

    # refactor in function
    if not current_msg['link'] in AMAZON_LOWERS_PRICES:
        AMAZON_LOWERS_PRICES.append(current_msg['link'])
        format_msg = f"{current_msg['Título']}\n{current_msg['Preço']}\n\n{current_msg['link']}"
        telegram.send_message(format_msg)


def main():
    """
    Insert yout code here
    """
    print('> Iniciando Smart TV...')
    telegram = TelegramBot(ROOT_DIR)
    # telegram.send_message("[SMART CRAWLER]\nEnviando os preços de smart TVs mais baixos...")
    
    print('> iniciando Casas Bahia...')
    crawl_casas_bahia(telegram)
    
    # print('> Iniciando Amazon')
    # crawl_amazon(telegram)
    
    # print('> Iniciando Magalu...')    
    # crawl_magalu(telegram)
    
    print('> Extração Finalizada!')
    

if __name__ == "__main__":
    schedule.every().day.at("12:00").do(main)
   
    while True:
        print('Esperando...', end="\r")
        schedule.run_pending()
        sleep(1)