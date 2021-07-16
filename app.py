from time import sleep
from utils.webdriver_handler import check_tag, dynamic_page
from utils.parser_handler import init_crawler, init_parser
from utils.setup import setSelenium
from utils.telegram import TelegramBot
import os
from math import inf
import schedule
from selenium.common.exceptions import NoSuchElementException



ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_price(price):
    final_price = price.split('R$')[-1]
    final_price = final_price.strip().replace(',','').replace('.','')
    return int(final_price)


def crawl_casas_bahia(telegram):
    driver = setSelenium(False)
    src_code = dynamic_page(driver, "https://www.casasbahia.com.br/c/?filtro=d41033&ordenacao=precoCrescente&icid=197947_hp_stc_c7_ps1_b0_pb2&origem=co&faixapreco=899to1413")
    driver.quit()

    print('> raspando preços...')
    soap = init_parser(src_code)

    try:
        tvs = soap.find('div', class_="styles__Wrapper-crf3j2-0 hMJXmq").find('div')
    
    except AttributeError:
        telegram.send_message('> Erro ao pegar os preços das casas bahia!')
        return

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
            return 'Não Disponível'


    url = "https://www.amazon.com.br/s?k=tvs+smarts&i=electronics&rh=n%3A16243822011%2Cp_n_size_browse-bin%3A17247917011&s=price-asc-rank&dc&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1626444567&rnid=16245418011&ref=sr_nr_p_n_size_browse-bin_2"

    soap = init_crawler(url)

    if soap == None:
        return

    container = soap.find('div', class_="s-main-slot s-result-list s-search-results sg-row")

    try:
        items = container.find_all('div', class_="sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col sg-col-4-of-20")

    except AttributeError:
        print('> Dados não carrregados..., tentand novamente!')
        crawl_amazon(telegram)
        return 
    
    lowest_tv = float(inf)
    current_msg = ''
    for item in items:
        title = item.find('h2', class_="a-size-mini a-spacing-none a-color-base s-line-clamp-4").text
        price = check_price(item)
        link = "https://www.amazon.com.br" + item.find('a')['href']

        msg = f"{title}\n{price}\n\n{link}"
        if price != 'Não Disponível':
            format_price = convert_price(price)
            
            if lowest_tv > format_price:
                lowest_tv = format_price
                current_msg = msg
    
    print(current_msg)
    telegram.send_message(current_msg)


def main():
    """
    Insert yout code here
    """
    print('> Iniciando Smart TV...')
    telegram = TelegramBot(ROOT_DIR)
    telegram.send_message("[SMART CRAWLER]\nEnviando os preços de smart TVs mais baixos...")
    print('> iniciando Casas Bahia...')
    crawl_casas_bahia(telegram)
    print('> Iniciando Amazon')
    crawl_amazon(telegram)
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
