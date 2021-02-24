import time
from selenium import webdriver
import pandas as pd
from datetime import date

__author__ = "Gabor Danielski"
__version__ = "0.1.0"
__version_upload_date__ = "24.02.2021"

TODAY = date.today()
BASE_URL = 'https://www.sofascore.com/tournament/basketball/usa/nba/132'
OUTPUT_FILE = 'output.csv'


class Scrapper:
    def __init__(self):
        webdriver_path = 'webdrivers/chromedriver.exe'
        webdriver_options = webdriver.ChromeOptions()
        webdriver_options.add_argument("--start-maximized")
        self.webdriver = webdriver.Chrome(webdriver_path, options=webdriver_options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.webdriver.quit()

    def get_data(self):
        self.webdriver.get(BASE_URL)
        time.sleep(3)
        self.webdriver.execute_script("window.scrollTo(0, 1000)")

        df = pd.DataFrame(
            columns=['Home team', 'Away team', 'Date', 'Result', 'Home points', 'Away points', 'Q1 home', 'Q2 home', 'Q3 home',
                     'Q4 home', 'Q5 home', 'Q1 away', 'Q2 away', 'Q3 away', 'Q4 away', 'Q5 away'])

        while True:

            games = self.webdriver.find_element_by_class_name('styles__EventListContent-b3g57w-2').find_elements_by_tag_name('a')
            games = games[1:]
            games = games[::-1]

            for g in games:
                game_date = g.find_element_by_tag_name('div').find_element_by_tag_name('div').find_element_by_tag_name('div').find_element_by_tag_name('div')
                home_team = g.find_element_by_tag_name('div').find_element_by_tag_name('div').find_elements_by_tag_name('div')[5]
                away_team = g.find_element_by_tag_name('div').find_element_by_tag_name('div').find_elements_by_tag_name('div')[6]
                home_points = g.find_element_by_tag_name('div').find_element_by_tag_name('div').find_elements_by_tag_name('div')[11]
                away_points = g.find_element_by_tag_name('div').find_element_by_tag_name('div').find_elements_by_tag_name('div')[12]
                scores = g.find_elements_by_tag_name('span')

                if len(home_points.text) < 1:
                    continue

                row = [home_team.text, away_team.text]

                if len(game_date.text) < 6:
                    row.append(TODAY.strftime("%d/%m/%Y"))
                else:
                    row.append(game_date.text)
                if int(home_points.text) > int(away_points.text):
                    row.append("H")
                else:
                    row.append("A")
                row.append(home_points.text)
                row.append(away_points.text)

                for s in scores:
                    if s.text == '':
                        row.append('')
                    else:
                        row.append(s.text)

                # print row to console
                print(row)

                s = pd.Series(row, index=['Home team', 'Away team', 'Date', 'Result', 'Home points', 'Away points', 'Q1 home',
                                          'Q2 home', 'Q3 home', 'Q4 home', 'Q5 home', 'Q1 away', 'Q2 away', 'Q3 away', 'Q4 away', 'Q5 away'])
                df = df.append(s, ignore_index=True)

            try:
                button = self.webdriver.find_element_by_class_name('list-wrapper').find_element_by_tag_name('div').find_element_by_tag_name('div')
                button.click()
            except:
                print("All games read or button not found")
                break

        print(df.head())
        print(df.shape)
        df.to_csv('output/' + OUTPUT_FILE)


if __name__ == '__main__':
    with Scrapper() as scrapper:
        scrapper.get_data()