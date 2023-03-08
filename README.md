
# Schoolware-api
A api for schoolware written in python

# capabilities
* get agenda points
* get scores
* get todo items

# install
* ```pip3 install schoolware-api```
* ```playwright install &&  playwright install-deps```

# example

```
from schoolware_api import schoolware_api

config = {"domain":"", "user":"", "password":""} #example domain: kov.schoolware.be user: name.lastname@leerling.kov.be password: password 

schoolware = schoolware_api.schoolware(config)

print(schoolware.todo())  # Returns all todo items
print(schoolware.punten()) # Returns all scores this schoolyear
print(schoolware.agenda()) # Returns agenda points today
print(schoolware.agenda(datum="2023-03-06 00:00:00")) # Returns agenda points for 2023-03-06
```
