import requests
from datetime import date, datetime, timedelta
from playwright.sync_api import sync_playwright
import time
from termcolor import colored
import threading




class schoolware:

    def __init__(self, config) -> None:
        self.config = config
        if("debug" in config):
            self.verbose = config["debug"]
        else:
            self.verbose = False
        if("verbose" in config):
            self.verbose = config["verbose"]
        else:
            self.verbose = False
        if("bg" in config):
            self.bg = config["bg"]
        else:
            self.bg = False
        
        if(self.bg):
            self.bg_p = threading.Thread(target=bg, args=(self,))
            print("start bg")
            self.bg_p.start()

        if("bot_token" in config):
            self.telegram_bg = threading.Thread(target=telegram_def, args=(self,))
            self.telegram_bg.start()
            
        self.domain = self.config["domain"]
        self.user = self.config["user"]
        self.password = self.config["password"]
        self.token = ""
        self.cookie = ""
        self.rooster = []
        self.todo_list = []
        self.scores = []
        if(self.verbose):
            print("getting startup token")
        self.check_if_valid()
        self.num_points = len(self.punten())
        
#Token&cookie stuff
    def get_new_token(self):
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            start_time = time.time()
            print(colored("• Starting get token", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0")
            page = context.new_page()
            page.goto(f"https://{self.domain}/webleerling/start.html#!fn=llagenda")
            page.locator('xpath=//*[@id="ext-comp-1014"]').click()
            page.get_by_role("textbox").fill(self.user)
            page.get_by_text("Next").click()
            page.get_by_placeholder("Password").fill(self.password)
            page.get_by_text("Sign In").click()
            page.wait_for_load_state()
            if(context.cookies()[0]["name"] == "FPWebSession"):
                self.token = context.cookies()[0]["value"]
                self.cookie = dict(FPWebSession=self.token)
            browser.close()
            ##########VERBOSE##########
            if(self.verbose):
                print(colored("#"*50, "grey"))
                end_time = time.time()
                print(colored(f"• Done getting token time:{end_time - start_time}", "green"))
                print(colored("#"*50, "grey"))
            ##########VERBOSE##########
            return self.token
    
    def check_if_valid(self):
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            start_time = time.time()
            print(colored(f"• Starting check token", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########

        r = requests.get(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/myschoolwareaccount", cookies=self.cookie)

        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            end_time = time.time()
            print(colored(f"• Done checking token time:{end_time - start_time}", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########
        if (r.status_code != 200):
            if(r.status_code == 401):
                self.get_new_token()
            else:
                raise "error with token"
        else:
            return True

#todo
    def todo(self):
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            start_time = time.time()
            print(colored("• Starting todo", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########

        self.check_if_valid()
        task_data = requests.get(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/AgendaPunt/?_dc=1665240724814&MinVan={date.today()}T00:00:00&IsTaakOfToets=true", cookies=self.cookie).json()["data"]
        self.todo_list = []

        for taak in task_data:
            if(taak["TypePunt"] == 1000):
                soort="Taak"
            elif(taak["TypePunt"] == 100):
                soort="toets"
            elif(taak["TypePunt"] == 101):
                soort="hertoets"

            vak= taak["VakNaam"]
            titel= taak["Titel"]
            onderwerp= taak["Commentaar"]
            eind_time = taak["Tot"].split(' ')[0]

            self.todo_list.append({
                "soort": soort,
                "vak": vak,
                "titel": titel,
                "onderwerp": onderwerp,
                "eind_time": eind_time
            })
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            end_time = time.time()
            print(colored(f"• Done todo time:{end_time - start_time}", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########
        return self.todo_list

#punten
    def punten(self):
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            start_time = time.time()
            print(colored("• Starting punten", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########
        self.check_if_valid()
        punten_data = requests.get(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/PuntenbladGridLeerling?&Leerling=15201&?BeoordelingMomentVan=1990-09-01+00:00:00", cookies=self.cookie).json()["data"]
        self.scores = []
        for vak in punten_data:

            for punt in vak["Beoordelingen"]:
                vak = punt["IngerichtVakNaamgebruiker"]
                DW = punt["DagelijksWerkCode"]
                totale_score = float(punt["BeoordelingMomentNoemer"])
                gewenste_score = float(punt["BeoordelingMomentGewenstAsString"])
                try:
                    behaalde_score = float(punt["BeoordelingWaarde"]["NumeriekAsString"])
                except:
                    behaalde_score = "n/a"
                publicatie_datum = punt["BeoordelingMomentPublicatieDatum"]
                datum = punt["BeoordelingMomentDatum"]
                titel = punt["BeoordelingMomentOmschrijving"]
                if(punt["BeoordelingMomentType_"] == "bmtToets"):
                    soort = "toets"
                else:
                    soort = "taak"

                self.scores.append({
                    "soort": soort,
                    "vak": vak,
                    "titel": titel,
                    "DW": DW,
                    "tot_sc": totale_score,
                    "gew_sc": gewenste_score,
                    "score": behaalde_score,
                    "datum": datum,
                    "pub_datum": publicatie_datum
                })
        self.scores.sort(key=lambda x: datetime.strptime(x['datum'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            end_time = time.time()
            print(colored(f"• Done punten time:{end_time - start_time}", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########
        return self.scores

#agenda
    def agenda(self, datum=""):
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            start_time = time.time()
            print(colored("• Starting agenda", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########
        self.check_if_valid()
        #begin en einde week
        day = str(date.today())
        dt = datetime.strptime(day, '%Y-%m-%d')
        start = (dt - timedelta(days=dt.weekday())).strftime('%Y-%m-%d')
        if(self.verbose):
            print(colored("#"*50, "grey"))
            print(f"start date: {start}")
            print(colored("#"*50, "grey"))
        end = ((dt - timedelta(days=dt.weekday())) + timedelta(days=6)).strftime('%Y-%m-%d')
        ####
        agenda_data = requests.get(f"https://kov.schoolware.be/webleerling/bin/server.fcgi/REST/AgendaPunt/?_MaxVan={end}&MinTot={start}", cookies=self.cookie).json()["data"]
        self.rooster = []
        for agenda in agenda_data:
            if(agenda["TypePunt"]==1 or agenda["TypePunt"]==2):
                self.rooster.append(agenda)
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            end_time = time.time()
            print(colored(f"• Done agenda time:{end_time - start_time}", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########
        return self.filter_rooster(self.rooster, datum)

    def filter_rooster(self, rooster, datum=""):
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            start_time = time.time()
            print(colored("• Starting filter_agenda", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########
        today = []
        if(datum == ""):
            datum = datetime.today()

        datum = str(datum).split(' ')[0]

        for agenda in rooster:
            if(str(agenda['Van'].split(' ')[0]) == datum):
                vak = agenda['VakNaam']
                lokaal = agenda['LokaalCode']
                titel = agenda['Titel']
                uur = agenda['Van'].split(' ')[1]

                today.append({
                    "vak": vak,
                    "lokaal": lokaal,
                    "titel": titel,
                    "uur": uur,
                    "skip": False,
                })
        today_filterd = []

        for index,agenda in enumerate(today):
            if(not agenda["skip"]):

                if(index == (len(today)-1)):
                    today_filterd.append(agenda)
                    continue


                if(agenda["uur"] == today[index+1]["uur"]):
                    if(agenda["vak"] == agenda["titel"]):
                        agenda["skip"] = True
                    elif(today[index+1]["vak"] == today[index+1]["titel"]):
                        today[index+1]["skip"] = True
                        today_filterd.append(agenda)
                else:
                    today_filterd.append(agenda)
        ##########VERBOSE##########
        if(self.verbose):
            print(colored("#"*50, "grey"))
            end_time = time.time()
            print(colored(f"• Done filter-agenda time:{end_time - start_time}", "green"))
            print(colored("#"*50, "grey"))
        ##########VERBOSE##########

        return today_filterd
            
#bg procces
def bg(self):
    from time import sleep
    if(self.verbose):
        print(colored("background procces started","blue"))
    while True:
        sleep(5*60)
        if(self.verbose):
            print(colored("background task: checking token","blue"))
        self.check_if_valid()

def telegram_def(self):
    import telegram
    from time import sleep
    import asyncio
    if(self.verbose):
        self.bot = telegram.Bot(self.config["bot_token"])
    print(colored("telegram started","blue"))
    while True:
        sleep(5*60)
        if(self.verbose):
            print(colored("telegram checking","blue"))
        num_now = len(self.punten())
        if(self.num_points < num_now):
            diff = num_now - self.num_points
            self.num_points = num_now
            
            asyncio.run(telegram_send_msg(self, diff))


async def telegram_send_msg(self, diff):
    async with self.bot:
        await self.bot.send_message(text=f'{diff} New point(s)', chat_id=self.config["chat_id"])