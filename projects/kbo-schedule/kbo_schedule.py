from bs4 import BeautifulSoup
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select




class GameCalCrawler:
   url = "https://www.koreabaseball.com/Schedule/Schedule.aspx"


   def crawling(self, month):
       options = Options()
       options.add_argument("--headless")
       options.add_argument("--no-sandbox")
       driver = webdriver.Chrome(options=options)


       driver.get(self.url)
       select = Select(driver.find_element(By.ID, "ddlMonth"))
       select.select_by_value(month)
       time.sleep(1)


       table = driver.find_element(By.CLASS_NAME, "tbl-type06")
       html = table.get_attribute("innerHTML")
       html = html.replace("<br>", " ")  # TV 같은 데이터 한 줄로 합치기
       soup = BeautifulSoup(html, "html.parser")
       rows_html = soup.find_all("tr")


       rows = []
       current_date = ""


       def is_time(s):
           return bool(re.match(r'^\d{1,2}:\d{2}$', s))


       def is_tv(s):
           # TV 채널명 패턴 확장: 예) SPO-2T, SPT-T, K-2T 등 포함
           return bool(re.match(r'^[A-Z0-9\-]{1,6}-\d*T$', s))


       def is_stadium(s):
           stadiums = {'잠실', '사직', '문학', '창원', '대전', '고척', '수원', '광주', '인천', '울산', '포항', '부산', '대구'}
           return s in stadiums


       def split_game_and_tv(text):
           # 경기명 끝에 TV 정보가 붙어 있으면 분리
           # ex) "KIA 2 vs 0 롯데 K-2T" -> ("KIA 2 vs 0 롯데", "K-2T")
           m = re.search(r'(.*?)(\b[A-Z0-9\-]{1,6}-\d*T)$', text)
           if m:
               game = m.group(1).strip()
               tv = m.group(2).strip()
               return game, tv
           else:
               return text, None


       for tr in rows_html:
           parts = tr.get_text(" ", strip=True).split()


           if not parts or parts[0] == "날짜":
               continue


           # 날짜 포함 행이면 날짜 갱신
           if parts[0].endswith(')'):
               current_date = parts[0]
               parts = parts[1:]


           game_info = {
               "날짜": current_date,
               "시간": "-",
               "경기": "-",
               "TV": "-",
               "라디오": "-",
               "구장": "-",
               "비고": "-"
           }


           # 시간 먼저 찾기 및 제거
           for p in parts[:]:
               if is_time(p):
                   game_info["시간"] = p
                   parts.remove(p)


           # 구장 찾기 및 제거
           for p in parts[:]:
               if is_stadium(p):
                   game_info["구장"] = p
                   parts.remove(p)


           # TV 후보 추출 및 제거
           tv_candidates = []
           for p in parts[:]:
               if is_tv(p):
                   tv_candidates.append(p)
                   parts.remove(p)


           if tv_candidates:
               game_info["TV"] = ", ".join(tv_candidates)
           else:
               game_info["TV"] = "-"


           # 라디오 정보 찾기 및 제거
           for p in parts[:]:
               if p.lower().startswith('radio') or p == '라디오' or p == '-':
                   game_info["라디오"] = p
                   parts.remove(p)


           # 비고 후보 찾기 및 제거 (우천취소 등 포함)
           notes = []
           for p in parts[:]:
               if p in {"리뷰", "하이라이트", "프리뷰", "우천취소"}:
                   notes.append(p)
                   parts.remove(p)


           if notes:
               game_info["비고"] = ", ".join(notes)
           else:
               game_info["비고"] = "-"


           # 남은 parts는 경기명 관련
           game_text = " ".join(parts).strip()
           # 경기명 끝에 TV 정보 붙어 있으면 분리
           game_text, extra_tv = split_game_and_tv(game_text)
           game_info["경기"] = game_text if game_text else "-"


           if extra_tv:
               if game_info["TV"] == "-" or not game_info["TV"]:
                   game_info["TV"] = extra_tv
               else:
                   game_info["TV"] += ", " + extra_tv


           rows.append(game_info)


       df = pd.DataFrame(rows).fillna("-")
       path = rf'C:\pca\{month}m_calender.json'
       df.to_json(path, force_ascii=False, orient='records', indent=4)


       driver.quit()
       return True




if __name__ == "__main__":
   crawler = GameCalCrawler()
   crawler.crawling("10")

