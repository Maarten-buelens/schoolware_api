import requests
from datetime import date, datetime, timedelta
from playwright.sync_api import sync_playwright
import time
from termcolor import colored
import threading
class schoolware:

    def __init__(self, config) -> None:
        """Pass config dict to init class
        Args:
        | Key | Description |
        | --- | --- |
        | domain | domain name of schoolware
        | user | school microsoft email
        | password | school microsoft password
        | bg | background procces to keep token valid
        | bot_token | telegram bot token to enable telegram bot
        | chat_id | id to send messages to
        | verbose | show a lot more info
        """
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
        self.scores_prev = self.scores
        
#Token&cookie stuff
    def get_new_token(self):
        ##########VERBOSE##########
        verbose_print(self,"get_token")
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
            verbose_end(self,"get_token")
            ##########VERBOSE##########
            return self.token
    
    def check_if_valid(self):
        ##########VERBOSE##########
        verbose_print(self,"check_token")
        ##########VERBOSE##########

        r = requests.get(f"https://{self.domain}/webleerling/bin/server.fcgi/REST/myschoolwareaccount", cookies=self.cookie)


        if (r.status_code != 200):
            if(r.status_code == 401):
                ##########VERBOSE##########
                verbose_end(self,"check_token invalid")
                ##########VERBOSE##########
                self.get_new_token()
            else:
                verbose_end(self,f"check_token error {r.status_code}")
                raise "error with token"
        else:
            ##########VERBOSE##########
            verbose_end(self,"check_token")
            ##########VERBOSE##########
            return True

#todo
    def todo(self):
        """gets all todo items from schoolware

        Returns:
            list: returns all todo items in a list ordered by descending date
        """
        ##########VERBOSE##########
        verbose_print(self,"todo")
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
        verbose_end(self,"todo")
        ##########VERBOSE##########
        return self.todo_list

#punten
    def punten(self):
        """Gets points from the whole year

        Returns:
            list: A list containing the points orderd by descending date
        """
        ##########VERBOSE##########
        verbose_print(self,"punten")
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
                dt = datetime.strptime(punt["BeoordelingMomentDatum"].split(' ')[0], '%Y-%m-%d')
                day = dt.strftime('%A')

                pub_dt = datetime.strptime(punt["BeoordelingMomentPublicatieDatum"].split(' ')[0], '%Y-%m-%d')
                pub_day = pub_dt.strftime('%A')
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
                    "pub_datum": publicatie_datum,
                    "day": day,
                    "pub_day": pub_day,
                })
        self.scores.sort(key=lambda x: datetime.strptime(x['datum'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        ##########VERBOSE##########
        verbose_end(self,"punten")
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
        verbose_print(self,"agenda")
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
        verbose_end(self,"agenda")
        ##########VERBOSE##########
        return self.filter_rooster(self.rooster, datum)

    def filter_rooster(self, rooster, datum=""):
        """Internal function to filter a agenda rooster of a given date

        Args:
            rooster (list): The agenda points to filter
            datum (str, optional): The date to filter agenda points for. Defaults to "".

        Returns:
            list: Filters agenda points for a given date and points
        """
        ##########VERBOSE##########
        verbose_print(self,"filter_agenda")
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
        verbose_end(self,"filter-agenda")
        ##########VERBOSE##########

        return today_filterd
    
    def telegram_manual_send(self, msg):
        """Manualy send a telegram message

        Args:
            msg (String): Message to send
        """
        import asyncio
        asyncio.run(telegram_send_msg(self, msg))

##########OTHER##########

#bg procces
def bg(self):
    """Function to keep token valid
    """
    from time import sleep
    if(self.verbose):
        print(colored("background procces started","blue"))
    while True:
        sleep(5*60)
        if(self.verbose):
            print(colored("background task: checking token","blue"))
        self.check_if_valid()
#telegram bot
def telegram_def(self):
    """The setup function for Telegram
    """
    import telegram
    from time import sleep
    import asyncio
    
    self.bot = telegram.Bot(self.config["bot_token"])
    print(colored("telegram started","blue"))
    while True:
        sleep(5*60)
        if(self.verbose):
            print(colored("telegram checking","blue"))
        scores_now = self.punten()
        num_now = len(scores_now)
        if(num_prev < num_now):
            diff_list = [i for i in scores_now if i not in scores_prev]
            diff = num_now - num_prev
            num_prev = num_now
            scores_prev = scores_now
            
            msg = f"{diff} New points for:\n"
            for item in diff_list:
                msg = msg + f"{item['vak']}\n"
            verbose_print(message=f"telegram send msg msg={msg}")
            asyncio.run(telegram_send_msg(self, msg))
            verbose_end(message="telegram send")

async def telegram_send_msg(self, msg):
    """Function to send a telegram message to a set message-id

    Args:
        msg (string): the message to send in telegram msg
    """
    async with self.bot:
        await self.bot.send_message(text=msg, chat_id=self.config["chat_id"])

##########VERBOSE##########
def verbose_print(self,message):
    """To print a message when verbose is set also times function

    Args:
        message (string): name of function to display
    """
    if(self.verbose):
        print(colored("#"*50, "grey"))
        self.start_time = time.time()
        print(colored(f"• starting {message}", "green"))
        print(colored("#"*50, "grey"))
def verbose_end(self,message):
    """Ends verbose_print with done and the time for the function

    Args:
        message (string): name of function to display
    """
    if(self.verbose):
        print(colored("#"*50, "grey"))
        end_time = time.time()
        print(colored(f"• Done {message} time:{end_time - self.start_time}", "green"))
        print(colored("#"*50, "grey"))
##########VERBOSE##########
