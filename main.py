from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from undetected_chromedriver.options import ChromeOptions
import undetected_chromedriver as uc
import selenium
import time
import parser_
import csv
import logging
import datetime
import os
from config import LOGIN_URL, BASE_URL, STARTING_ROW, AMOUNT_TO_PARSE, LOGIN, PASSWORD


def initialize_directories_and_files():
    cwd = os.getcwd()
    dirs = [os.path.join(cwd, "data"), os.path.join(cwd, "logs")]
    files = [os.path.join(cwd, "data", "nomenclature.csv")]
    for dir_ in dirs:
        if not os.path.exists(dir_):
            os.mkdir(dir_)
    for file in files:
        if not os.path.exists(dir_):
            with open(file, "w"):
                ...


def login(driver: uc.Chrome) -> None:
    driver.get(LOGIN_URL)
    try:
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        driver.find_element(By.NAME, "email").send_keys(LOGIN)
        driver.find_element(By.CLASS_NAME, "btn-green").click()
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_elements(By.CLASS_NAME, "btn")[1].click()
    except Exception as ex:
        logging.error("Log in error", exc_info=True)


def get_item_page(item_id: str, driver: uc.Chrome) -> None | str:
    try:
        driver.get(BASE_URL + item_id)
    except Exception as ex:
        logging.error("Attribute Error", exc_info=True)
        return None
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[2]/div[2]/div/section/div[5]/div[1]/span")
            )
        )
    except Exception as ex:
        logging.error("Attribute Error", exc_info=True)
        return None
    try:
        ActionChains(driver).move_to_element(
            driver.find_element(
                By.XPATH, "/html/body/div[2]/div[2]/div/section/div[5]/div[1]/span"
            )
        ).perform()
        time.sleep(2)
    except selenium.common.exceptions.NoSuchElementException as ex:
        logging.error("Attribute Error", exc_info=True)
        return None
    return driver.page_source


def main(driver: uc.Chrome) -> None:
    login(driver)
    with open("./data/nomenclature.csv", "r") as f:
        reader = csv.reader(f)
        counter = 0
        for row in reader:
            counter += 1
            if not row[1] or (counter < STARTING_ROW):
                continue
            print(row[1], counter)
            html = get_item_page(row[1], driver=driver)
            if html is None:
                continue
            try:
                parser_.parse_all(
                    part_number=row[0],
                    market_place_id=row[1],
                    market="Wildberries",
                    html=html,
                )
            except AttributeError as er:
                logging.error("Attribute Error", exc_info=True)
                continue
            logging.info(f"Successfully parsed {row[1]}")
            if counter == AMOUNT_TO_PARSE:
                return
    driver.quit()


if __name__ == "__main__":
    initialize_directories_and_files()
    print(STARTING_ROW)
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(
            os.getcwd(),
            "logs",
            f"{datetime.datetime.utcnow().strftime('%d-%m-%Y %H-%M-%S')}.log",
        ),
        filemode="w",
    )
    options = ChromeOptions()
    options.add_argument("--disable-web-security")
    driver = uc.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    main(driver)
    driver.quit()
