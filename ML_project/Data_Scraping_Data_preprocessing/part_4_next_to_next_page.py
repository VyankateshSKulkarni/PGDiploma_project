import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import quote  # For URL encoding

driver = webdriver.Firefox()

df = pd.read_csv('Honor_with_ratings_and_feature_hrefs.csv')
new_data = []

features = {
    "Camera": "Camera_href",
    "Battery": "Battery_href",
    "Display": "Display_href",
    "Design": "Design_href",
    "Performance": "performance_href"
}

for index, row in df.iterrows():
    row_data = row.tolist() 

    for feature, href_column in features.items():
        url = row[href_column]

        if pd.isna(url) or url == 'N/A' or not isinstance(url, str):
            print(f"Skipping invalid URL for {feature} at index {index}: {url}")
            row_data.extend(["N/A", "N/A", "N/A", "N/A"]) 
            continue

        try:
            encoded_url = quote(url, safe=":/?&=")

            driver.get(encoded_url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div._61Da9i'))
            )

            try:
                overall_rating = driver.find_element(By.CSS_SELECTOR, "text._2DdnFS").text
            except NoSuchElementException:
                overall_rating = "N/A"

            try:
                positive_score = driver.find_element(By.CSS_SELECTOR, "span.WtBCuZ").text
            except NoSuchElementException:
                positive_score = "N/A"

            try:
                negative_score = driver.find_element(By.CSS_SELECTOR, 'span._9VjbDx').text
            except NoSuchElementException:
                negative_score = "N/A"

            unique_comments = set()
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, "div.ZmyHeo div")
                for element in comment_elements:
                    comment = element.text.strip()
                    if comment and comment not in unique_comments:
                        unique_comments.add(comment)
            except NoSuchElementException:
                pass

            comments = list(unique_comments) if unique_comments else ["N/A"]

            row_data.extend([overall_rating, positive_score, negative_score, comments])

        except TimeoutException:
            print(f"Timeout occurred for {feature} at URL {encoded_url}")
            row_data.extend(['Timeout', 'Timeout', 'Timeout', 'Timeout'])
        except Exception as e:
            print(f"An error occurred for {feature} at URL {encoded_url}: {e}")
            row_data.extend(['Error', 'Error', 'Error', 'Error'])

    new_data.append(row_data)

driver.quit()

new_columns = df.columns.tolist()
for feature in features.keys():
    new_columns.extend([
        f"{feature}_Overall_Rating",
        f"{feature}_Positive_Score",
        f"{feature}_Negative_Score",
        f"{feature}_Comments"
    ])

result_df = pd.DataFrame(new_data, columns=new_columns)

result_df.to_csv('Honor_with_ratings_and_feature_hrefs.csv', index=False)

print("Scraping completed. Results saved...")
