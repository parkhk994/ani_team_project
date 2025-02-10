from selenium import webdriver # 모든 브라우저
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

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
sleep_sec = 3
df_titles = pd.DataFrame()
for z in range(1, 5):  # 4번 페이지 더보기 시도
    url = 'https://ridibooks.com/category/books/1650?adult_exclude=y&page={}'.format(z)
    driver.get(url)
    time.sleep(2)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(1)

    # 페이지의 모든 책 요소 찾기
    book_elements = driver.find_elements(By.XPATH,
                                         '//*[@id="__next"]/main/div/section/ul[3]/li/div/div[2]/div/div[1]/a')

    for i, element in enumerate(book_elements, 1):
        try:
            print(i, i, i)
            titles = []
            reviews = []

            # 새 탭에서 책 열기
            open_in_new_tab(driver, element)
            print(i)
            time.sleep(sleep_sec)

            title_xpath = '//*[@id="ISLANDS__Header"]/div/div/div/div[2]/h1'

            # 리뷰 개수 확인
            try:
                review_cnt_xpath = '//*[@id="detail_review"]/div[3]/button[2]/span[2]'
                review_cnt_element = driver.find_element(By.XPATH, review_cnt_xpath)
                review_cnt = review_cnt_element.text
                review_cnt = int(re.sub(r'\D', '', review_cnt))
                print(f"리뷰 개수: {review_cnt}개")
            except Exception as e:
                print(f"리뷰 개수 확인 중 오류: {e}")
                # 현재 탭 닫기
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            # 타이틀 추출
            try:
                title = driver.find_element(By.XPATH, title_xpath).text
                title = re.sub('"', '', title)  # 모든 종류의 큰따옴표 제거
                titles.append(title)
                print(f"현재 작품 타이틀: {title} 입니다.")
            except Exception as e:
                print(f"타이틀 추출 중 오류: {e}")
                # 현재 탭 닫기
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            # 리뷰 개수 조건 확인
            if review_cnt < 11:
                print(f"리뷰 개수 {review_cnt}개: 다음 작품으로 넘어갑니다.")
                # 현재 탭 닫기
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(5)
                continue

            # 더보기 버튼 클릭
            for _ in range(4):  # 4번 페이지 더보기 시도
                try:
                    button_xpath_more = '//*[@id="detail_review"]/div[5]/button/span'
                    driver.find_element(By.XPATH, button_xpath_more).click()
                    time.sleep(sleep_sec)
                    print('더보기 완료')
                except Exception as e:
                    print(f"더보기 버튼 클릭 중 예외 발생: {e}")
                    break

            # 리뷰 추출
            for j in range(1, 51):
                try:
                    if j <= 10:
                        review_CSS_selector = '#detail_review > ul > li:nth-child({}) > div.rigrid-3s6awr > p'.format(j)
                    else:
                        review_CSS_selector = '#detail_review > ul > li:nth-child({}) > div.rigrid-1hjvtyt-Jg > p'.format(
                            j)

                    review = driver.find_element(By.CSS_SELECTOR, review_CSS_selector).text
                    review = re.compile('[^가-힣 ]').sub(' ', review)
                    reviews.append(review)
                    print(f"현재 작품 타이틀: {title}")
                    print(f"현재 작품 리뷰: {review}")
                except Exception as e:
                    print(f"리뷰 추출 실패 - j={j}: {e}")
                    continue

            # 현재 탭 닫기
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # 데이터프레임 생성 및 병합
            data = {
                'Title': [title] * len(reviews),
                'Review': reviews
            }
            df_section = pd.DataFrame(data)
            df_titles = pd.concat([df_titles, df_section], ignore_index=True)
            time.sleep(sleep_sec)

        except Exception as e:
            print(f"작품 처리 중 전체 오류 발생: {e}")
            try:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
            continue

print(df_titles.head())
df_titles.info()
df_titles.to_csv('./crawling_data/webnovel_{}_{}.csv'.format(200, datetime.datetime.now().strftime('%Y%m%d')),
                 index=False)

time.sleep(10)
driver.close()