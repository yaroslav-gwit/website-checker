# Python based website cheker
## Functionality
1. SSL date check: tool will let you know if your website's certificate has expired or is about to expire.
2. JSON output for tools like Zabbix.
3. Table output for humans.

## Features that will be developed soon
- Site response time check
- Site status code check
- Check for a certain string on a webpage
- Zabbix integration
- SNI website checks
#### There should be a FastAPI endpoint exposed at some point too
##### The feature list will include:
- Adding a website to the list
- Removing a website from the list
- Checking a list of websites
- Checking a signle website

## Compatibility
Python 3.10+

### If you are running Debian or Ubuntu, it's better to use a docker container:
https://hub.docker.com/r/mexicanrancher/website-checker

## Installation
1. Clone this repo
```
git clone https://github.com/yaroslav-gwit/website-checker.git
```
2. Cd into the project's folder and install python dependencies
```
cd website-checker
python3 -m pip install -r requirements.txt
```

## Screenshots
