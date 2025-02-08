from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

driver = webdriver.Firefox()

product_list = []

for i in range(1, 7):
    flipkart_url = f"https://www.flipkart.com/search?q=honor+mobile&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}"

    # Open the Flipkart URL
    driver.get(flipkart_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.KzDlHZ'))
        )

        products = driver.find_elements(By.CSS_SELECTOR, "a.CGtC98")  # Find product links

        for product in products:
            href = product.get_attribute("href")

            product_name = product.find_element(By.CSS_SELECTOR, 'div.KzDlHZ').text
            product_rating = product.find_element(By.CSS_SELECTOR, 'div.XQDdHH').text
            rating_number = product.find_element(By.CSS_SELECTOR, "span.Wphh3N").text
            information = [item.text for item in product.find_elements(By.CSS_SELECTOR, "ul.G4BRas li")]
            price = product.find_element(By.CSS_SELECTOR, 'div.Nx9bqj').text

            print(
                f"Product: {product_name}, Rating: {product_rating}, Rating Count: {rating_number}, Info: {information}, Price: {price}, href: {href}"
            )

            product_list.append([product_name, product_rating, rating_number, information, price, href])

    except Exception as e:
        print(f"An error occurred: {e}")

driver.quit()

df = pd.DataFrame(product_list, columns=['Product Name', 'Rating', 'Rating Count', 'Information', 'Price', 'href'])
df.to_csv('Honor.csv', index=False)
