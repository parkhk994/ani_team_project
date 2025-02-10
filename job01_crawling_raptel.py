from selenium import webdriver # 모든 브라우저
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import re
import time
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
options.add_argument('user_agent=' + user_agent)
options.add_argument('lang=ko_KR')
options.add_argument("--blink-settings=imagesEnabled=false") # 이미지 비활성화


service = ChromeService(executable_path=ChromeDriverManager().install()) # 브라우저 install
driver = webdriver.Chrome(service=service, options=options)



category = ['Titles', 'Review']

def open_in_new_tab(driver, element):
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[-1])

def srolling():
    for _ in range(10):  # 50번 페이지 다운 시도
        # 페이지의 body 요소를 찾아서 end 키를 보냄
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(1)


# for z in range(1):

df_titles = pd.DataFrame()
url = 'https://laftel.net/finder'
driver.get(url)
time.sleep(2)

sleep_sec = 3

# 인기 순 버튼
button_CSS_pop = '#root > div.sc-f0aad20d-0.cJKdpk > div.sc-314e188f-0.hqsXVO > div.sc-314e188f-2.hVHfbj > div > div > div > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div.sc-b650993-1.dPuSyZ > div.sc-42a3c8f1-0.eiatWD > div > div > div.sc-29d1736d-0.fkHAgS > div > div'
button = driver.find_element(By.CSS_SELECTOR, button_CSS_pop)
driver.execute_script("arguments[0].scrollIntoView(true);", button)
time.sleep(1)
# JavaScript로 클릭 시도
driver.execute_script("arguments[0].click();", button)
print("인기순 버튼 클릭")
time.sleep(2)  # 페이지 로딩 대기

#리뷰 많은순 버튼
button_CSS_review = '#root > div.sc-f0aad20d-0.cJKdpk > div.sc-314e188f-0.hqsXVO > div.sc-314e188f-2.hVHfbj > div > div > div > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div.sc-b650993-1.dPuSyZ > div.sc-42a3c8f1-0.eiatWD > div > div > div.sc-29d1736d-0.fkHAgS > div.sc-29d1736d-3.bblvNc > div:nth-child(6) > div.sc-29d1736d-8.fDdkop'
button = driver.find_element(By.CSS_SELECTOR, button_CSS_review)
driver.execute_script("arguments[0].scrollIntoView(true);", button)
time.sleep(1)
# JavaScript로 클릭 시도
driver.execute_script("arguments[0].click();", button)
print("리뷰순 버튼 클릭")
time.sleep(2)  # 페이지 로딩 대기

# end 전 옆 배경 누르기
button_xpath_background = '//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div[1]/div[2]/div/div/div/div[2]/div'
driver.find_element(By.XPATH, button_xpath_background).click()
time.sleep(sleep_sec)

srolling()
input('아무버튼을 눌러주세요')

for i in range(1,401):

    titles = []
    reviews = []

    button_xpath = '//*[@id="contents"]/div/div/div[3]/div[2]/div[{}]/a/div/div[1]/div[1]/img'.format(i) #
    button_xpath1 = '//*[@id="review"]' # 리뷰 버튼
    button_xpath3 = '//*[@id="content__body"]/div' #

    element = driver.find_element(By.XPATH, button_xpath)
    open_in_new_tab(driver, element)
    print(i)
    time.sleep(1)

    # driver.find_element(By.XPATH, button_xpath).click()
    # time.sleep(1)
    try:
        driver.find_element(By.XPATH, button_xpath1).click()
        time.sleep(1)
        driver.find_element(By.XPATH, button_xpath3).click()
        time.sleep(1)
    except:
        # time.sleep(50)
        print('error')
        driver.back()
        srolling()
        element = driver.find_element(By.XPATH, button_xpath)
        open_in_new_tab(driver, element)
        print(i)
        time.sleep(1)
        driver.find_element(By.XPATH, button_xpath1).click()
        time.sleep(1)
        driver.find_element(By.XPATH, button_xpath3).click()
        time.sleep(1)


    title_xpath = '//*[@id="contents"]/div[1]/div[2]/div[1]/div[1]/h2'

    try :
        title = driver.find_element(By.XPATH,title_xpath).text
        # title = re.compile('[^가-힣 ]').sub(' ', title)
        titles.append(title)
        #print(title)
    except: #예외처리
        print('i')
        print(i)


    # 스크롤 다운

    for _ in range(5):  # 5번 페이지 다운 시도
        # 페이지의 body 요소를 찾아서 PAGE_DOWN 키를 보냄
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(1)


    for j in range(1,51):

        try:
            review_xpath = '//*[@id="contents"]/div[5]/section[2]/div/article[{}]/div[3]/a/h5'.format(j)
            review = driver.find_element(By.XPATH, review_xpath).text
            review = re.compile('[^가-힣 ]').sub(' ', review)
            reviews.append(review)
        except:
            print("j")
            print(j)

    # 현재 탭(새로 열린 탭) 닫기
    driver.close()

    # 원래 탭으로 돌아가기
    driver.switch_to.window(driver.window_handles[0])

    # 각 영화마다 제목과 리뷰를 매칭하여 데이터프레임 생성
    data = {
        'Title': [title] * len(reviews),  # 리뷰 개수만큼 제목 반복
        'Review': reviews
    }
    df_section = pd.DataFrame(data)
    df_titles = pd.concat([df_titles, df_section], ignore_index=True)

print(df_titles.head())
df_titles.info()
df_titles.to_csv('./crawling_data/laftel_{}_{}.csv'.format(400,
datetime.datetime.now().strftime('%Y%m%d')), index=False) # 나노second단위 받은 시간으로 오늘 날짜로 바꿔서 저장

time.sleep(10)
driver.close()
