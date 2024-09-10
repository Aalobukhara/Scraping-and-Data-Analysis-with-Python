from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
from datetime import datetime
import time


print("import successful")



# considers the page loaded as soon as the DOM is loaded, ignoring other assets like ads or images
options = Options()
options.page_load_strategy = 'eager'



# Initialize Firefox gecko driver instance
driver = webdriver.Firefox(options=options)
print('webdriver initialised')



try:
    driver.get("https://uk.investing.com/commodities/us-sugar-no11-historical-data")
    
    
    
    # Maximizes window for bigger viewport
    driver.maximize_window()
    print('window maximized')
    
    
    
    # Gets the current URL
    current_url = driver.current_url

    # Check the status code of the main website
    response = requests.get(current_url)
    if response.status_code == 200:
        print("Main website loaded successfully.")
    
    
    
    
    # Wait for the element to be loaded
    wait = WebDriverWait(driver, 8)
    element = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space()='US Sugar #11 Futures - Oct 24 (SBV4)']")))

    # Scroll the element into view using JS
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

    # scroll wait
    time.sleep(2)


    timeframe_dropdown = WebDriverWait(driver, 15).until(
            # EC.element_to_be_clickable((By.ID, 'timeframe-dropdown-id'))
        EC.element_to_be_clickable((By.CLASS_NAME, 'historical-data-v2_selection-arrow__3mX7U'))
    )
    timeframe_dropdown.click()
    
    time.sleep(5)
    print("sleeping one complete, clicked the dropdown menu div")  
    
    # weekly_option = driver.find_element(By.XPATH, "//*[contains(@class, 'historical-data-v2_menu-row-text__ZgtVH') and contains(text(), 'weekly')]")
    # weekly_option.click()
    
    
    
    # Waitin  for the dynamic div that contains options to appear
    options_div = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, 'historical-data-v2_menu__uJ2BW')))

    # Select a specific option by its text (text is inside a span)
    option_text = 'Weekly'
    option = options_div.find_element(By.XPATH, f"//div[contains(@class, 'historical-data-v2_menu__uJ2BW')]//div[contains(@class, 'historical-data-v2_menu-row__oRAlf')]//span[text()='{option_text}']")
    # option = options_div.find_element(By.XPATH, f"//div[contains(@class, 'historical-data-v2_menu__uJ2BW')]//div[contains(@class, 'historical-data-v2_menu-row__oRAlf')]//span[text()='{option_text}']]")
    option.click()
    
    
    
    
    time.sleep(10)
    print("sleeping two complete, chose the weekly option from the dropdown")
    
    ################################################################################################################################################################################3
    #################################################################################################################
    
    
    
    
    
    # Extract the table data
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//table[@class='freeze-column-w-1 w-full overflow-x-auto text-xs leading-4']"))
    )
    rows = table.find_elements(By.XPATH, f".//tr")

    data = []
    for row in rows[1:]:  # Skippin the header row
        cols = row.find_elements(By.XPATH, f".//td")
        if len(cols) >= 2:
            date = cols[0].text
            price = cols[1].text
            data.append({"Product Date": date, "Price": price})
finally:
    driver.quit()
    
print("table data extraction complete")

# Create DataFrame
df = pd.DataFrame(data)
df['Product Name'] = 'Sugar'  # Added product name column
print("dataframe created")

# duplicates and NaN values
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)
print('duplicate and NaN vslues removd')

# # Adding Day of week column
df['Product Date'] = pd.to_datetime(df['Product Date'])
df['Day'] = df['Product Date'].dt.day_name()

df['Product Date'] = df['Product Date'].dt.strftime('%d-%m-%Y')

print("day of week column added")


# Convert USD to INR (using a sample API, replace with an actual currency conversion API)
def usd_to_inr(usd_price):
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/USD")
    exchange_rate = response.json()['rates']['INR']
    return float(usd_price) * exchange_rate

print("currency excahneg api called")

df['Price'] = df['Price'].str.replace(',', '').astype(float)
df['Final Price (INR)'] = df['Price'].apply(usd_to_inr)

print("currency conversion completed and INR column added")


# Rearrange columns in the required order
df = df[['Product Name','Price','Product Date', 'Day','Final Price (INR)' ]]



df.to_excel("Output.xlsx", index=False)
print('outputfilesaved')


print("Data has been successfully scraped, processed, and saved to Output.xlsx")


