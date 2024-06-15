import os
import time
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from colorama import Fore, init
from webdriver_manager.chrome import ChromeDriverManager

init(autoreset=True)


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_welcome_message():
    messages = [
        r"""
          _    _  ____   _____  _____ ______ _      _____ _____ _   _ 
         | |  | |/ __ \ / ____|/ ____|  ____| |    |  __ \_   _| \ | |
         | |__| | |  | | (___ | |  __| |__  | |    | |  | || | |  \| |
         |  __  | |  | |\___ \| | |_ |  __| | |    | |  | || | | . ` |
         | |  | | |__| |____) | |__| | |____| |____| |__| || |_| |\  |
         |_|  |_|\____/|_____/ \_____|______|______|_____/_____|_| \_|

        """,
        r"""
         __     __      _____ _____ __  __  _____ _____ 
         \ \   / //\   |  __ \_   _|  \/  |/ ____|_   _|
          \ \_/ //  \  | |__) || | | \  / | |      | |  
           \   // /\ \ |  ___/ | | | |\/| | |      | |  
            | |/ ____ \| |    _| |_| |  | | |____ _| |_ 
            |_/_/    \_\_|   |_____|_|  |_|\_____|_____|

        """,
        r"""
         __     __       _____ ______ ______ 
         \ \   / //\    / ____|  ____|  ____|
          \ \_/ //  \  | (___ | |__  | |__   
           \   // /\ \  \___ \|  __| |  __|  
            | |/ ____ \ ____) | |____| |     
            |_/_/    \_\_____/|______|_|     

        """
    ]

    for message in messages:
        print(Fore.GREEN + message + Fore.RESET)
        input("Enter tuşuna basın...")
        clear_terminal()


def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return file_path


def get_user_choice():
    print("""
    1. Ürünlerini Favorile
    2. Ürünlerini Sepete Ekle
    3. Mağazayı Takip Et
    4. Hepsini Yap
    """)
    choice = input("Seçeneklerden birini seçiniz: ")
    return choice


show_welcome_message()
choice = get_user_choice()

wait_minutes = int(input("Kaç Dakika Aralıkla Olsun: "))

accounts_file_path = select_file("Merhaba! Hesaplar için metin dosyasını seçin",
                                 [("Text files", "*.txt"), ("All files", "*.*")])
if not accounts_file_path:
    print("Hesap dosyası seçilmedi. Program sonlandırılıyor.")
    exit()

product_urls = []
store_urls = []

if choice in ['1', '2', '4']:
    urls_file_path = select_file("Ürün link dosyasını seçin", [("Text files", "*.txt"), ("All files", "*.*")])
    if not urls_file_path:
        print("Ürün dosyası seçilmedi. Program sonlandırılıyor.")
        exit()
    with open(urls_file_path, 'r') as file:
        product_urls = [url.strip() for url in file if url.strip()]

if choice in ['3', '4']:
    store_urls_file_path = select_file("Mağaza link dosyasını seçin", [("Text files", "*.txt"), ("All files", "*.*")])
    if not store_urls_file_path:
        print("Mağaza dosyası seçilmedi. Program sonlandırılıyor.")
        exit()
    with open(store_urls_file_path, 'r') as file:
        store_urls = [url.strip() for url in file if url.strip()]

accounts = []
with open(accounts_file_path, 'r') as file:
    for line in file:
        parts = line.strip().split(":")
        if len(parts) == 2:
            email, password = parts
            accounts.append((email, password))
        else:
            print(f"Hatalı format: {line.strip()}. Bu satır atlanıyor.", Fore.RED)

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-extensions')
options.add_argument('--no-sandbox')
options.add_argument('--disable-infobars')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-browser-side-navigation')
options.add_argument('--disable-gpu')

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


def login_and_process(driver, email, password, product_urls, store_urls, choice):
    success_count = 0
    try:
        driver.get("https://www.trendyol.com/giris?cb=%2F")

        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-email")))
        email_input.send_keys(email)

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-password-input")))
        password_input.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="login-register"]/div[3]/div[1]/form/button')))
        login_button.click()

        time.sleep(2)

        if choice in ['1', '4']:
            for url in product_urls:
                driver.get(url)
                try:
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'fv')))
                    favori_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'fv')))
                    driver.execute_script("arguments[0].click();", favori_button)

                    print(f"{email}: Ürün favorilere eklendi", Fore.GREEN)
                    success_count += 1

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"{email}: Ürün favorilere eklenemedi. Hata: {str(e)}", Fore.RED)

        if choice in ['2', '4']:
            for url in product_urls:
                driver.get(url)
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'add-to-basket')))
                    sepetekle_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'add-to-basket')))
                    driver.execute_script("arguments[0].click();", sepetekle_button)

                    print(f"{email}: Ürün sepete eklendi", Fore.GREEN)
                    success_count += 1

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"{email}: Ürün sepete eklenemedi. Hata: {str(e)}", Fore.RED)

        if choice in ['3', '4']:
            for url in store_urls:
                driver.get(url)
                try:
                    follow_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="seller-store-header"]/div/div/div[1]/div[3]/div[1]/div')))
                    driver.execute_script("arguments[0].click();", follow_button)

                    print(f"{email}: Mağaza takip edildi", Fore.GREEN)
                    success_count += 1

                except (TimeoutException, NoSuchElementException):
                    try:
                        follow_button = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//*[@id="seller-store-header"]/div/div/div[1]/div[3]/div[1]')))
                        driver.execute_script("arguments[0].click();", follow_button)

                        print(f"{email}: Mağaza takip edildi", Fore.GREEN)
                        success_count += 1
                    except (TimeoutException, NoSuchElementException) as e:
                        print(f"{email}: Mağaza takip edilemedi. Hata: {str(e)}", Fore.RED)

        driver.get("https://www.trendyol.com/authentication/logout")

    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        print(f"{email}: Giriş veya işlem sırasında hata oluştu. Hata: {str(e)}", Fore.RED)

    return success_count


total_success_count = 0
total_urls = len(product_urls) + len(store_urls)

for email, password in accounts:
    total_success_count += login_and_process(driver, email, password, product_urls, store_urls, choice)
    print(f"{wait_minutes} dakika bekleniyor...", Fore.YELLOW)
    time.sleep(wait_minutes * 60)

if total_success_count == total_urls * len(accounts):
    print("Tüm işlemler tamamlandı", Fore.GREEN)
else:
    print("Tüm işlemler tamamlanamadı", Fore.RED)

driver.quit()
