
# Schoolware-api
A api for schoolware written in python

# intall
* ``` pip3 install schoolware-api ```
* ``` playwright install &&  playwright install-deps```

# example

```
from schoolware_api import schoolware_api

config = {"domain":"","password":"","user":""}

schoolware = schoolware_api.schoolware(config)
print(schoolware.taken())
```