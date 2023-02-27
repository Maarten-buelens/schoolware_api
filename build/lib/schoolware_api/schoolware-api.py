class schoolware_api:

    def __init__(self, config) -> None:
        import requests
        import datetime
        import json
        from playwright.sync_api import sync_playwright
        import time
        config = json.loads(config)
        token = ""

    def get_new_token(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0")
            page = context.new_page()
            page.goto("https://{}/webleerling/start.html#!fn=llagenda".format(config["domain"]))
            page.locator('xpath=//*[@id="ext-comp-1014"]').click()
            page.get_by_role("textbox").fill(config["user"])
            page.get_by_text("Next").click()
            page.get_by_placeholder("Password").fill(config["password"])
            page.get_by_text("Sign In").click()
            page.wait_for_load_state()
            if(context.cookies()[0]["name"] == "FPWebSession"):
                self.token = context.cookies()[0]["value"]
            browser.close()

