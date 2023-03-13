
# Schoolware-api
An api for schoolware written in python

# capabilities
* get agenda points
* get scores
* get todo items
* send telegram message for new scores

# config
* domain: domain name of schoolware
* user: school microsoft email
* password: school microsoft password
* bg: background procces to keep token valid
* bot_token: telegram bot token to enable telegram bot
* chat_id: id to send messages to
* verbose: show a lot more info

# install
* ```pip3 install schoolware_api termcolor --upgrade ```
* ```playwright install &&  playwright install-deps```

## optional
* ```pip3 install python-telegram-bot```

# simple example

```
from schoolware_api import schoolware_api

config = {"domain":"", "user":"", "password":""} #example domain: kov.schoolware.be user: name.lastname@leerling.kov.be password: password 

schoolware = schoolware_api.schoolware(config)

print(schoolware.todo())  # Returns all todo items
print(schoolware.punten()) # Returns all scores this schoolyear
print(schoolware.agenda()) # Returns agenda points today
print(schoolware.agenda(datum="2023-03-06 00:00:00")) # Returns agenda points for 2023-03-06
```
# complete example
```
from schoolware_api import schoolware_api
{"domain":"","password":"","user":"","verbose": false, "bg": true, "bot_token": "", "chat_id": ""}

schoolware = schoolware_api.schoolware(config)

same as other
```
