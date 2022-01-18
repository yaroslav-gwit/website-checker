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


## Installation
### Docker
Pull the container:
```
docker pull mexicanrancher/website-checker
```

Run the software:
```
docker run -it --rm mexicanrancher/website-checker /usr/src/app/website_monitor.py --help
docker run -it --rm mexicanrancher/website-checker /usr/src/app/website_monitor.py check-site gateway-it.com
```
Output:
```
╒════════════════╤═════════════════════╤══════════════╕
│ Site address   │ SSL Cert EOL Date   │ Status       │
╞════════════════╪═════════════════════╪══════════════╡
│ gateway-it.com │ 2022-03-21 12:37:44 │ Site is okay │
╘════════════════╧═════════════════════╧══════════════╛
```

Download and edit file `site_list.yaml`, then execute the command below 
```
docker run -it --rm -v /root/site_list.yaml:/usr/src/app/site_list.yaml mexicanrancher/website-checker /usr/src/app/website_monitor.py yaml-file
```
Output:
```
╒════╤══════════════════════════╤═════════════════════╤═══════════════════════╤════════════════╤═══════════════╕
│    │ Site address             │ SSL Cert EOL Date   │ Status                │ Owner          │ Description   │
╞════╪══════════════════════════╪═════════════════════╪═══════════════════════╪════════════════╪═══════════════╡
│  1 │ gateway-it.com           │ 2022-01-12 18:35:15 │ SSL cert has expired! │ Yaroslav Koisa │ -             │
├────┼──────────────────────────┼─────────────────────┼───────────────────────┼────────────────┼───────────────┤
│  2 │ google.com               │ 2022-03-21 06:02:10 │ Site is okay          │ Google         │ -             │
├────┼──────────────────────────┼─────────────────────┼───────────────────────┼────────────────┼───────────────┤
│  3 │ yahoo.com                │ 2022-06-15 23:59:59 │ Site is okay          │ N/A            │ -             │
╘════╧══════════════════════════╧═════════════════════╧═══════════════════════╧════════════════╧═══════════════╛
```

YAML file used in this example:
```
---
websites:
  - site_name: google.com
    site_port: 443
    amber_days: 30
    site_owner: Google

  - site_name: nextcloud.gateway-it.com
    site_port: 443
    amber_days: 30
    site_owner: Yaroslav Koisa

  - site_name: yahoo.com
```

The last example shown here, will include `--json-output` flag. It is mostly used for Zabbix integration, or any other system where JSON output format is supported.
```
docker run -it --rm -v /root/site_list.yaml:/usr/src/app/site_list.yaml mexicanrancher/website-checker /usr/src/app/website_monitor.py yaml-file --json-output
#or
docker run -it --rm mexicanrancher/website-checker /usr/src/app/website_monitor.py check-site gateway-it.com
```

Example output:
```
#For the YAML-FILE option
[{"site_name": "google.com", "ssl_cert_eol": "2022-03-21 06:02:10", "status": 1, "owner": "Google"}, {"site_name": "gateway-it.com", "ssl_cert_eol": "2022-01-12 18:35:15", "status": 2, "owner": "Yaroslav Koisa"}, {"site_name": "yahoo.com", "ssl_cert_eol": "2022-06-15 23:59:59", "status": 1}]

#For the CHECK-SITE option
{"site_name": "gateway-it.com", "ssl_eol": "2022-03-21 12:37:44", "site_status": 1}
```

### Manual (recommended for develovers, or experienced Python users)
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
