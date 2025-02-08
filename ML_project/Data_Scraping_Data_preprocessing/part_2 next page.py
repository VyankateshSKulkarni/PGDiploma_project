import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox()

df = pd.read_csv('Honor.csv')

new_data = []

for index, row in df.iterrows():
    url = row['href']
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.wNNofW ul:last-child'))
        )

        rating_counts = driver.find_elements(By.CSS_SELECTOR, "div.wNNofW ul:last-child li div.BArk-j")

        if len(rating_counts) == 5:
            five_star, four_star, three_star, two_star, one_star = [count.text for count in rating_counts]
        else:
            five_star = four_star = three_star = two_star = one_star = 'N/A'

        feature_elements = driver.find_elements(By.CSS_SELECTOR, "div.Nwhkb3 div.row a.col-3-12")
        camera_href = battery_href = display_href = design_href = 'N/A'

        for feature in feature_elements:
            feature_name = feature.find_element(By.CSS_SELECTOR, "div.NTiEl0").text
            feature_href = feature.get_attribute('href')

            if feature_name == "Camera":
                camera_href = feature_href
            elif feature_name == "Battery":
                battery_href = feature_href
            elif feature_name == "Display":
                display_href = feature_href
            elif feature_name == "Design":
                design_href = feature_href


        print(f'5★: {five_star}, 4★: {four_star}, 3★: {three_star}, 2★: {two_star}, 1★: {one_star}')
        print(f'Camera href: {camera_href}')
        print(f'Battery href: {battery_href}')
        print(f'Display href: {display_href}')
        print(f'Design href: {design_href}')

        new_row = row.tolist() + [five_star, four_star, three_star, two_star, one_star, camera_href, battery_href,
                                  display_href, design_href]
        new_data.append(new_row)

    except Exception as e:
        print(f"An error occurred for URL {url}: {e}")
        new_data.append(row.tolist() + ['N/A'] * 9)  

driver.quit()

columns = df.columns.tolist() + ['5_star', '4_star', '3_star', '2_star', '1_star', 'Camera_href', 'Battery_href',
                                 'Display_href', 'Design_href']
result_df = pd.DataFrame(new_data, columns=columns)

result_df.to_csv('Honor_with_ratings_and_feature_hrefs.csv', index=False)

print("Scraping completed. Results saved to 'with_ratings_and_feature_hrefs.csv'")
