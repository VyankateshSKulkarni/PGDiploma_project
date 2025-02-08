import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

driver = webdriver.Firefox()

df = pd.read_csv('Honor_with_ratings_and_feature_hrefs.csv')
new_data = []

for index, row in df.iterrows():
    url = row['Camera_href']

    if pd.isna(url) or url == 'N/A' or not isinstance(url, str):
        print(f"Skipping invalid URL at index {index}: {url}")
        continue

    try:
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cPHDOP.col-12-12'))
        )

        overall_href = performance_href = 'N/A'

        links = driver.find_elements(By.CSS_SELECTOR, 'div.cPHDOP.col-12-12 div[class="+uoMff"] a')

        for link in links:
            try:
                feature_name = link.find_element(By.TAG_NAME, "span").text.strip()
                feature_href = link.get_attribute('href')

                if feature_name == "Overall":
                    overall_href = feature_href
                elif feature_name == "Performance":
                    performance_href = feature_href

            except NoSuchElementException:
                print(f"Could not locate span inside anchor for URL: {url}")
                continue

        new_row = row.tolist() + [overall_href, performance_href]
        new_data.append(new_row)

    except TimeoutException:
        print(f"Timeout occurred for URL {url}")
        new_data.append(row.tolist() + ['Timeout', 'Timeout'])
    except Exception as e:
        print(f"An error occurred for URL {url}: {e}")
        new_data.append(row.tolist() + ['N/A', 'N/A'])

driver.quit()

new_data_df = pd.DataFrame(new_data, columns=df.columns.tolist() + ['overall_href', 'performance_href'])

result_df = pd.concat([df.reset_index(drop=True), new_data_df.drop(columns=df.columns)], axis=1)

result_df.to_csv('Honor_with_ratings_and_feature_hrefs.csv', index=False)

print("Scraping completed. Results saved to 'with_camera_ratings_and_comments.csv'")
