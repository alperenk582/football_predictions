import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

class FootballGuess():
    def __init__(self):
        self.options=Options()
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--ignore-ssl-errors")
        self.service=Service(ChromeDriverManager().install())
        self.browser=webdriver.Chrome(service=self.service,options=self.options)
        self.url="https://arsiv.mackolik.com/Standings/Default.aspx?sId="
        self.wait=WebDriverWait(self.browser,10)

    def removeAds(self):
        self.browser.execute_script("""
            var iframe = document.getElementById('mobinter');
            if (iframe) iframe.remove();
            var adhouse = document.querySelector('adhouse');
            if (adhouse) adhouse.remove();
        """)

    def guessChamp(self,league):
        self.browser.get(f"{self.url}{league}")
        team_names=[]
        seasons=[]
        team_points=[]
        for season_idx in range(1,6):
            self.removeAds()

        
            season_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "cboSeason")))
            self.browser.execute_script("arguments[0].click;",season_btn)

            self.browser.execute_script("arguments[0].scrollIntoView(true);", season_btn)
            self.browser.execute_script("arguments[0].click();", season_btn)

            options = season_btn.find_elements(By.TAG_NAME, "option")

            if season_idx > len(options):
                break

            season_name=options[season_idx].text.strip()
            options[season_idx].click()

            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"tbody tr")))
            teams=self.browser.find_elements(By.CSS_SELECTOR,"tbody tr")

            for team in teams:
                name_links=team.find_elements(By.CSS_SELECTOR,"a[class='style3']")
                point_links=team.find_elements(By.CSS_SELECTOR,"td")

                if name_links and point_links:
                    team_name=name_links[0].text.strip()
                    team_point=point_links[9].text.strip()

                    team_points.append(team_point)

                    team_names.append(team_name)

                    seasons.append(season_name)

        np_team_points=np.array(team_points)
        np_seasons=np.array(seasons)
        np_teams=np.array(team_names)
        guess_arr=np.stack((np_seasons,np_teams,np_team_points),axis=1)

        seasons_uniqe=np.unique(guess_arr[:,0])[::-1]
        season_points=[]
        grouped=[]
        for season in seasons_uniqe:
            season_rows=guess_arr[guess_arr[:,0]==season]
            grouped.append(season_rows)
            season_points.append(season_rows[:,2].astype(int))

        # check for diffrent team numbers in the league
        filled=[]
        max_team_num=max(sr.shape[0] for sr in grouped)
        for sr in grouped:
            team_num=sr.shape[0]
            if team_num < max_team_num:
                diff=max_team_num - team_num
                fill=np.array([["","","0"]] * diff)
                sr=np.vstack([sr,fill])
            filled.append(sr)

        data_3D=np.array(filled)

        champions=data_3D[:,0,1]
     
        guess_points_champ=[2.5,2,1.5,1,0.5]
        guess_scores={}
        for indx,champ in enumerate(champions):
            guess_point=guess_points_champ[indx]
            guess_scores[champ]=guess_scores.get(champ,0) + guess_point

        champ_point_average=0
        second_point_average=0
        third_point_average=0
        fourth_point_average=0
        fifth_point_average=0

        for points in season_points:
            champ_point_average+=points[0]
            second_point_average+=points[1]
            third_point_average+=points[2]
            fourth_point_average+=points[3]
            fifth_point_average+=points[4]                

        champ_point_average//=5
        second_point_average//=5
        third_point_average//=5
        fourth_point_average//=5
        fifth_point_average//=5

        guess_scores2={}
        for season_data in data_3D:
            for team_data in season_data:
                name=team_data[1]
                point=int(team_data[2])

                if champ_point_average+5 >= point >= champ_point_average-3:
                    guess_scores2[name]=guess_scores2.get(name,0) + 3.5

                elif second_point_average+3 >= point >= second_point_average-4:
                    guess_scores2[name]=guess_scores2.get(name,0)+3

                elif third_point_average+4 >= point >= third_point_average-2:
                    guess_scores2[name]=guess_scores2.get(name,0)+2.5

                elif fourth_point_average+3 >= point >= fourth_point_average-1:
                    guess_scores2[name]=guess_scores2.get(name,0) + 2

                elif fifth_point_average+2 >= point >= fifth_point_average-5:
                    guess_scores2[name]=guess_scores2.get(name,0) + 1.5

        final_scores={}
        for team_n,scroe in guess_scores.items():
            final_scores[team_n]=final_scores.get(team_n,0)+scroe

        for team_n,score in guess_scores2.items():
            final_scores[team_n]=final_scores.get(team_n,0)+score

        sorted_final = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        for sort,(sorted_team,_) in enumerate(sorted_final,start=1):
            if sort==1:
                print(f"predicted champion: {sorted_team}")
            else:
                print(sorted_team)


guess=FootballGuess()
while True:
    choosing=input("q- exit\n1- guess new champion\n")
    if choosing=="q":
        guess.browser.quit()
        break

    elif choosing=="1":
        url_codes={
            "1":"67180",
            "2":"70368",
            "3":"70184",
            "4":"70371",
            "5":"70351",
            "6":"70381"
        }
        league=input("enter league:\n1- Premier League\n2- Laliga\n3- Serie A\n4- Bundesliga\n5- League 1\n6- Türkiye Super League\n")
        if league=="1":
            league=url_codes["1"]
        elif league=="2":
            league=url_codes["2"]
        elif league=="3":
            league=url_codes["3"]
        elif league=="4":
            league=url_codes["4"]
        elif league=="5":
            league=url_codes["5"]
        elif league=="6":
            league=url_codes["6"]
        guess.guessChamp(league)
