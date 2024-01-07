import requests
from datetime import date, datetime, timedelta
from playwright.sync_api import sync_playwright
import threading
import logging
import json

class schoolware:

    def __init__(self, config) -> None:
        """Pass config dict to init class
        Args:
        | Key | Description |
        | --- | --- |
        | domain | domain name of schoolware
        | user | school microsoft email
        | password | school microsoft password
        | bot_token | telegram bot token to enable telegram bot
        | chat_id | id to send messages to
        | verbose | show a some more info
        | debug | show a lot more info
        """

        
        self.config = config
        if("debug" in config):
            self.debug = config["debug"]
            if(self.debug):
                logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.DEBUG)
        else:
            self.debug = False

        if("verbose" in config):
            self.verbose = config["verbose"]
            if(self.verbose):
                logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.INFO)
            else:
                logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.WARNING)
        else:
            self.verbose = False
            logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.WARNING)

        if("schoolware_login" in config):
            self.schoolware_login = config["schoolware_login"]
        else:
            self.schoolware_login = False

        if("telegram_msg" in config):
            self.telegram_msg = config["telegram_msg"]
        else:
            self.telegram_msg = ""
        self.domain = self.config["domain"]
        self.user = self.config["user"]
        self.password = self.config["password"]
        
        self.token = ""
        self.cookie = ""
        self.rooster = []
        self.todo_list = []
        self.scores = []
        self.verbose_print(message="starting schoolware_api",level=1)        

        if("bot_token" in config):
            self.prev_scores = self.punten()
            self.telegram_bg = threading.Thread(target=self.telegram_setup, args=(0,))
            self.telegram_bg.start()
        
#Token&cookie stuff
    def get_new_token(self):
        ##########VERBOSE##########
        self.verbose_print("get_token")
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
            self.verbose_end("get_token")
            ##########VERBOSE##########
            return self.token
    
    def get_new_token_schoolware(self):
        ##########VERBOSE##########
        self.verbose_print("get_token_schoolware")
        ##########VERBOSE##########
        url = f"https://{self.domain}/webleerling/bin/server.fcgi/RPC/ROUTER/"
        payload = "{action: \"WisaUserAPI\", method: \"Authenticate\", data: [\""+self.user+"\",\""+self.password+"\"], type: \"rpc\", tid: 1}"
        r = requests.request("POST", url, data=payload)
        self.cookie = requests.utils.dict_from_cookiejar(r.cookies)
        self.token = self.cookie["FPWebSession"]
        ##########VERBOSE##########
        self.verbose_end("get_token_schoolware")
        ##########VERBOSE##########
        return self.token

    def get_token(self):
        self.make_request("https://{self.domain}/webleerling/bin/server.fcgi/REST/myschoolwareaccount")
        return self.token


    def make_request(self,url):
        r = requests.get(url, cookies=self.cookie)

        if (r.status_code != 200):
            if(r.status_code == 401):
                ##########VERBOSE##########
                self.verbose_end("check_token invalid")
                ##########VERBOSE##########
                if(not self.schoolware_login):
                    self.verbose_end("Using Microsoft login")
                    self.get_new_token()
                    r = requests.get(url, cookies=self.cookie)
                else:
                    self.verbose_end("Using Schoolware login")
                    self.get_new_token_schoolware()
                    r = requests.get(url, cookies=self.cookie)
            else:
                self.verbose_end(f"check_token error {r.status_code}")
                raise "error with token"
        else:
            ##########VERBOSE##########
            self.verbose_end("check_token")
            ##########VERBOSE##########
        return r



#todo
    def todo(self):
        """gets all todo items from schoolware

        Returns:
            list: returns all todo items in a list ordered by descending date
        """
        ##########VERBOSE##########
        self.verbose_print("todo")
        ##########VERBOSE##########

        task_data = self.make_request(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/AgendaPunt/?_dc=1665240724814&MinVan={date.today()}T00:00:00&IsTaakOfToets=true").json()["data"]
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
            dt = datetime.strptime(taak["Tot"].split(' ')[0], '%Y-%m-%d')
            day = dt.strftime('%A')

            self.todo_list.append({
                "soort": soort,
                "vak": vak,
                "titel": titel,
                "onderwerp": onderwerp,
                "eind_time": eind_time,
                "day": day
            })
        ##########VERBOSE##########
        self.verbose_end("todo")
        ##########VERBOSE##########
        return self.todo_list

#punten
    def punten(self):
        """Gets points from the whole year

        Returns:
            list: A list containing the points orderd by descending date
        """
        ##########VERBOSE##########
        self.verbose_print("punten")
        ##########VERBOSE##########

        punten_data = self.make_request(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/PuntenbladGridLeerling?BeoordelingMomentVan=1990-09-01+00:00:00")
        punten_data = punten_data.json()["data"]
        self.scores = []
        for vak in punten_data:

            for punt in vak["Beoordelingen"]:
                try:
                    vak = punt["IngerichtVakNaamgebruiker"]
                    try:
                        DW = punt["DagelijksWerkCode"]
                        EX = None
                    except:
                        DW = None
                        EX = punt["ExamenCode"]
                    totale_score = float(punt["BeoordelingMomentNoemer"])
                    gewenste_score = float(punt["BeoordelingMomentGewenstAsString"])
                    try:
                        behaalde_score = float(punt["BeoordelingWaarde"]["NumeriekAsString"])
                    except:
                        behaalde_score = "n/a"
                    publicatie_datum = punt["BeoordelingMomentPublicatieDatum"]
                    datum = punt["BeoordelingMomentDatum"]
                    titel = punt["BeoordelingMomentOmschrijving"]
                    dt = datetime.strptime(punt["BeoordelingMomentDatum"].split(' ')[0], '%Y-%m-%d')
                    day = dt.strftime('%A')

                    pub_dt = datetime.strptime(punt["BeoordelingMomentPublicatieDatum"].split(' ')[0], '%Y-%m-%d')
                    pub_day = pub_dt.strftime('%A')
                    if(punt["BeoordelingMomentType_"] == "bmtToets"):
                        soort = "toets"
                    else:
                        soort = "taak"

                    try:
                        cat = punt["BeoordelingMomentCategorieOmschrijving"]
                    except:
                        cat = None

                    self.scores.append({
                        "soort": soort,
                        "vak": vak,
                        "titel": titel,
                        "DW": DW,
                        "EX": EX,
                        "tot_sc": totale_score,
                        "gew_sc": gewenste_score,
                        "score": behaalde_score,
                        "datum": datum,
                        "pub_datum": publicatie_datum,
                        "day": day,
                        "pub_day": pub_day,
                        "cat": cat
                    })
                except:
                    pass
        self.scores.sort(key=lambda x: datetime.strptime(x['datum'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        ##########VERBOSE##########
        self.verbose_end("punten")
        ##########VERBOSE##########
        return self.scores

#agenda
    def agenda(self, datum=""):
        """Gets all agenda points of a given date from schoolware

        Args:
            datum (str, optional): Date to get agenda for. Defaults to "".

        Returns:
            list: returns output from filter_agenda
        """
        ##########VERBOSE##########
        self.verbose_print("agenda")
        ##########VERBOSE##########
        #begin en einde week
        day = str(date.today())
        if(datum == ""):
            dt = datetime.strptime(day, '%Y-%m-%d')
        else:
            datum = str(datum).split(' ')[0]
            dt = datetime.strptime(datum, '%Y-%m-%d')
        start = dt.strftime("%Y-%m-%d")
        end =  (dt + timedelta(days=1)).strftime("%Y-%m-%d")
        ####
        agenda_data = self.make_request(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/AgendaPunt/?MaxVan={end}&MinTot={start}").json()["data"]
        self.rooster = []
        for agenda in agenda_data:
            if(agenda["TypePunt"]==1 or agenda["TypePunt"]==2):
                self.rooster.append(agenda)
        ##########VERBOSE##########
        self.verbose_end("agenda")
        ##########VERBOSE##########
        return self.filter_rooster(self.rooster, datum)

    def agenda_week(self, datum=""):
        days = []
        day = str(date.today())
        if(datum == ""):
            dt = datetime.strptime(day, '%Y-%m-%d')
        else:
            datum = str(datum).split(' ')[0]
            dt = datetime.strptime(datum, '%Y-%m-%d')

    
        #get start of week
        days_to_subtract = dt.weekday()
        start = dt - timedelta(days=days_to_subtract)

        for i in range(5):
            day_week = start + timedelta(days=i)
            days.append({
                "date": day_week.strftime("%m/%d"),
                "points":self.agenda(day_week)
                })
        self.verbose_print(days)
        return days


    def filter_rooster(self, rooster, datum=""):
        """Internal function to filter a agenda rooster of a given date

        Args:
            rooster (list): The agenda points to filter
            datum (str, optional): The date to filter agenda points for. Defaults to "".

        Returns:
            list: Filters agenda points for a given date and points
        """
        ##########VERBOSE##########
        self.verbose_print("filter_agenda")
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
                commentaar = agenda["Commentaar"]
                if(commentaar != ""):
                    commentaar = json.loads(commentaar)    
                    commentaar = commentaar["leerlingen"]
                    
                uur = agenda['Van'].split(' ')[1]

                today.append({
                    "vak": vak,
                    "lokaal": lokaal,
                    "titel": titel,
                    "commentaar": commentaar,
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
        self.verbose_end("filter-agenda")
        ##########VERBOSE##########

        return today_filterd
    
    ##########OTHER##########

    #telegram bot
    def telegram_setup(self, none):
        """The setup function for Telegram
        """
        import telegram
        from time import sleep
        self.bot = telegram.Bot(self.config["bot_token"])
        self.prev_scores = self.scores
        while True:
            sleep(5*60)
            try:
                if(self.verbose):
                    self.verbose_print(message=f"telegram checking")
                
                self.telegram_point_diff()
            except:
                logging.warning(f"error in telegram loop")

    def telegram_point_diff(self):
            import asyncio

            new_scores = self.punten()


            if(len(self.prev_scores) < len(new_scores)):
                
                    diff_list = [i for i in new_scores if i not in self.prev_scores]
                    diff = len(diff_list)
                    self.prev_scores = new_scores
                    
                    if(self.telegram_msg == ""):
                        msg = f"{diff} New points:\n"
                        for item in diff_list:
                            msg = msg + f"{item['vak']} {item['titel']}: {float(item['score']) * float(item['tot_sc']) if item['score'] != 'n/a' else 'n/a'}/{item['tot_sc']}\n"
                    else:
                        eval(self.telegram_msg)

                    self.verbose_print(message=f"telegram send msg msg={msg}", level=1)
                    asyncio.run(self.telegram_send_msg(msg))


    async def telegram_send_msg(self, msg):
        """Function to send a telegram message to a set message-id

        Args:
            msg (string): the message to send in telegram msg
        """
        async with self.bot:
            await self.bot.send_message(text=msg, chat_id=self.config["chat_id"])

    ##########VERBOSE##########
    def verbose_print(self,message, level=0):
        """To print a message when verbose is set also times function

        Args:
            message (string): name of function to display
        """
        if(self.verbose):
            logging.debug(f"starting {message}")

        if(level == 1):
            logging.info(f"{message}")

    def verbose_end(self,message):
        """Ends self.verbose_print with done and the time for the function

        Args:
            message (string): name of function to display
        """
        if(self.verbose):
            logging.debug(f"Done {message}")

    ##########VERBOSE##########
