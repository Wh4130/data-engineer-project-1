import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# * Cronjob that wakes up the streamlit apps
urls = {"bubble_tea": "https://dssq-bubble-tea-m9jzmospevfsw8uh2ncz4o.streamlit.app/",
        "easyessay_master": "https://easyessay-literature-review-toolkit-wally.streamlit.app/",
        "easyessay_guest": "https://easyessay-literature-review-toolkit-guest.streamlit.app/",
        "iii_Demand_Foresight_Tools (dev)": "https://demand-foresight-trend-report-generator-dev.streamlit.app/",
        "iii_Demand_Foresight_Tools (main)": "https://demand-foresight-trend-report-generator-main.streamlit.app/",
        "media_dashboard": "https://taiwan-media-dashboard-tool.streamlit.app/"}

def awaken_sleeping_apps():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")           # 無頭模式（不開視窗）
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # 避免 shared memory 不夠用
    options.add_argument("--disable-gpu") 

    print("Logging streamlit apps...")

    driver = webdriver.Chrome(options)

    for title, url in urls.items():
        # Open a web page
        driver.get(url)
        time.sleep(5)

        try:
            driver.find_element(By.TAG_NAME, 'button').click()
            time.sleep(1)
            print(f"'{title}' is awaken!")
        except Exception as E:
            print(E)

        time.sleep(2)

    # Close the browser
    driver.quit()
