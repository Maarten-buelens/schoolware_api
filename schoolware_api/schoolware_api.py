import requests
from datetime import date, datetime, timedelta
from playwright.sync_api import sync_playwright

class schoolware:

    def __init__(self, config) -> None:
        self.config = config
        if("debug" in config):
            self.debug = config["debug"]
        else:
            self.debug = False

        if("verbose" in config):
            self.verbose = config["verbose"]
        else:
            self.verbose = False
        self.domain = self.config["domain"]
        self.user = self.config["user"]
        self.password = self.config["password"]
        self.token = ""
        self.cookie = ""
        self.rooster = []
        self.todo = []
        self.scores = []
        if(self.verbose):
            print("getting startup token")
        self.check_if_valid()
        
#Token&cookie stuff
    def get_new_token(self):
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
            return self.token
    
    def check_if_valid(self):
        r = requests.get(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/AgendaPunt", cookies=self.cookie)
        if (r.status_code != 200):
            if(r.status_code == 401):
                self.get_new_token()
            else:
                raise "error with token"
        else:
            return True

#todo
    def todo(self):
        self.check_if_valid()
        task_data = requests.get(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/AgendaPunt/?_dc=1665240724814&MinVan={date.today()}T00:00:00&IsTaakOfToets=true", cookies=self.cookie).json()["data"]
        self.todo = []

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

            self.todo.append({
                "soort": soort,
                "vak": vak,
                "titel": titel,
                "onderwerp": onderwerp,
                "eind_time": eind_time
            })
        return self.todo

#punten
    def punten(self):
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
        return self.scores

#agenda
    def agenda(self, datum=""):
        self.check_if_valid()
        #begin en einde week
        day = str(date.today())
        dt = datetime.strptime(day, '%Y-%m-%d')
        start = (dt - timedelta(days=dt.weekday())).strftime('%Y-%m-%d')
        if(self.debug):
            print("#"*50)
            print(f"start date: {start}")
            print("#"*50)
        end = ((dt - timedelta(days=dt.weekday())) + timedelta(days=6)).strftime('%Y-%m-%d')
        ####
        agenda_data = requests.get(f"https://kov.schoolware.be/webleerling/bin/server.fcgi/REST/AgendaPunt/?_MaxVan={end}&MinTot={start}", cookies=self.cookie).json()["data"]
        self.rooster = []
        for agenda in agenda_data:
            if(agenda["TypePunt"]==1 or agenda["TypePunt"]==2):
                # if(self.debug):
                #     print("#"*50)
                #     print(f"start filter date: {start}")
                #     print(f"end filter date: {end}")
                #     print("#"*50)
                self.rooster.append(agenda)

        return self.filter_rooster(self.rooster, datum)

    def filter_rooster(self, rooster, datum=""):
        today = []
        if(datum == ""):
            datum = datetime.today()
            if(self.debug):
                datum = datetime.strptime("2023-03-06", '%Y-%m-%d')

        datum = str(datum).split(' ')[0]
        if(self.debug):
            print("#"*50)
            print(f"filter date: {datum}")
            print("#"*50)
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





        if(self.debug):
            print("#"*50)
            print(f"Today: {today}")
            print(f"Today len: {len(today)}")
            print("#"*50)
            print(f"Today_filted: {today_filterd}")
            print(f"Today_filterd len: {len(today_filterd)}")
            print("#"*50)



            
        return today_filterd
            


