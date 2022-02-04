#!/usr/bin/env python3
#Script requires >=python3.10
from datetime import datetime
from datetime import timedelta
import typer
import OpenSSL
import ssl
import yaml
import json
from tabulate import tabulate
import sys
import os
import re
# import requests


app = typer.Typer(context_settings=dict(max_content_width=800))



class ReadWriteYaml:
    """ This class reads and writes YAML config file """

    def __init__(self, yaml_file_location="site_list.yaml", yaml_input_dict = None):
        site_list_yaml_location = yaml_file_location

        if not os.path.exists(site_list_yaml_location):
            print("The database file doesn't exits!")
            sys.exit(1)

        with open(site_list_yaml_location, 'r') as file:
            self.site_list_yaml = yaml.safe_load(file)

        self.site_list_yaml_location = site_list_yaml_location
        self.yaml_input_dict = yaml_input_dict

        if os.stat(site_list_yaml_location).st_size != 0:
            self.website_list = self.site_list_yaml["websites"]
        else:
            self.website_list = []


    def write(self):
        if self.yaml_input_dict:
            with open(self.site_list_yaml_location, 'w') as file:
                yaml.dump(self.yaml_input_dict, file, sort_keys=False)
        else:
            print("There is no input (dictionary) to work with!")
            sys.exit(119)



class GetSiteInfo:
    """ This class gets the info about the website """

    def __init__(self, site_address, site_port=443, amber_days=30):
        self.site_address = site_address
        self.site_port = site_port
        self.amber_days = timedelta(amber_days)

        """
        site response collection -- future code:
        import response
        response = requests.get("https://gateway-it.com/", timeout=3)
        respTime = response.elapsed.total_seconds()
        currDate = datetime.now()[:-7]
        print(currDate + " " + respTime)
        """

        if not self.site_address:
            print("Please set the 'site_address' variable!")
            exit(1)

        try:
            cert = ssl.get_server_certificate(addr=(self.site_address, self.site_port), timeout=3)
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            self.expiration_date = datetime.strptime(x509.get_notAfter().decode("utf-8")[:-1], "%Y%m%d%H%M%S")
            self.status_unreachable = False
        except:
            self.expiration_date = "N/A"
            self.status_unreachable = True


    def ssl_expiry_date_machine(self):
        """
        Status codes:
        1 - site is okay
        2 - ssl cert is expired
        3 - ssl cert is close to expiring
        4 - site is not reachable
        """
        if self.status_unreachable:
            return [self.site_address, self.expiration_date, 4]
        elif self.expiration_date < datetime.now():
            return [self.site_address, self.expiration_date, 2]
        elif self.expiration_date < (datetime.now() + self.amber_days):
            return [self.site_address, self.expiration_date, 3]
        elif (self.expiration_date - self.amber_days) > datetime.now():
            return [self.site_address, self.expiration_date, 1]


    def ssl_expiry_date_human(self):
        if self.status_unreachable:
            status_unreachable = typer.style("Site is not reachable!!", fg=typer.colors.WHITE, bg=typer.colors.RED, bold=False)
            site_unreachable = typer.style(self.site_address, fg=typer.colors.WHITE, bg=typer.colors.RED, bold=False)
            return [site_unreachable, self.expiration_date, status_unreachable]
        elif self.expiration_date < datetime.now():
            site_expired = typer.style(self.site_address, fg=typer.colors.RED, bold=True)
            status_expired = typer.style("SSL cert has expired!", fg=typer.colors.RED, bold=True)
            return [site_expired, self.expiration_date, status_expired]
        elif self.expiration_date < (datetime.now() + self.amber_days):
            site_amber = typer.style(self.site_address, fg=typer.colors.YELLOW, bold=False)
            status_amber = typer.style("SSL cert is close to expiring", fg=typer.colors.YELLOW, bold=False)
            return [site_amber, self.expiration_date, status_amber]
        elif (self.expiration_date - self.amber_days) > datetime.now():
            status_good = "Site is okay"
            return [self.site_address, self.expiration_date, status_good]


    def check_status_code(self):
        return self


    def check_page_string(self):
        return self



class GiveInfo:
    """ This class will form the info and pass it over to user """

    @staticmethod
    def single_site_table_output(site_name, site_port=443, amber_days=30):
        checked_sites_list = []
        checked_sites_list_call = GetSiteInfo(site_name, site_port, amber_days)
        checked_sites_list.append(checked_sites_list_call.ssl_expiry_date_human())

        table_header = ["Site address", "SSL Cert EOL Date", "Status"]
        checked_sites_list.insert(0, table_header)

        checked_sites_list = checked_sites_list
        return tabulate(checked_sites_list, headers="firstrow", tablefmt="fancy_grid")


    @staticmethod
    def single_site_json_output(site_name, site_port=443, amber_days=30):
        get_site_info_output = GetSiteInfo(site_name, site_port, amber_days).ssl_expiry_date_machine()
        json_output = {"site_name": get_site_info_output[0], "ssl_eol": str(get_site_info_output[1]),
                       "site_status": get_site_info_output[2]}
        json_output = json.dumps(json_output)
        return json_output


    @staticmethod
    def yaml_table_output(yaml_file_location):
        checked_sites_list = []
        owners_list = []
        description_list = []
        for website in ReadWriteYaml(yaml_file_location).website_list:
            checked_sites_list_call = GetSiteInfo(website.get("site_name"), website.get("site_port", 443),
                                                  website.get("amber_days", 30))
            checked_sites_list.append(checked_sites_list_call.ssl_expiry_date_human())
            owners_list.append(website.get("site_owner", "N/A"))
            description_list.append(website.get("description", "-"))

        ''' Add owners and description to every site entry '''
        for item in checked_sites_list:
            item.append(owners_list[checked_sites_list.index(item)])
            item.append(description_list[checked_sites_list.index(item)])

        checked_sites_list.sort()

        table_header = ["Site address", "SSL Cert EOL Date", "Status", "Owner", "Description"]
        checked_sites_list.insert(0, table_header)

        checked_sites_list = checked_sites_list
        return tabulate(checked_sites_list, headers="firstrow", showindex=range(1, len(checked_sites_list)),
                        tablefmt="fancy_grid")


    @staticmethod
    def yaml_json_output(yaml_file_location):
        checked_sites_list = []
        owners_list = []
        description_list = []
        for website in ReadWriteYaml(yaml_file_location).website_list:
            checked_sites_list_call = GetSiteInfo(website.get("site_name"), website.get("site_port", 443),
                                                  website.get("amber_days", 30))
            checked_sites_list.append(checked_sites_list_call.ssl_expiry_date_machine())
            owners_list.append(website.get("site_owner", "N/A"))
            description_list.append(website.get("description", "-"))

        ''' Add owners and description to every site entry '''
        for item in checked_sites_list:
            item.append(owners_list[checked_sites_list.index(item)])
            item.append(description_list[checked_sites_list.index(item)])

        checked_sites_list.sort()
        list_of_dicts = []
        for item in checked_sites_list:
            _temp_dict = {}
            _temp_dict["site_name"] = item[0]
            if item[1] != "N/A":
                _temp_dict["ssl_cert_eol"] = str(item[1])
            _temp_dict["status"] = item[2]
            if item[3] != "N/A":
                _temp_dict["owner"] = item[3]
            if item[4] != "-":
                _temp_dict["description"] = item[4]
            list_of_dicts.append(_temp_dict)

        json_output = json.dumps(list_of_dicts)
        return json_output


""" Section below is responsible for the CLI input/output """

@app.command()
def site_check(site_address: str = typer.Argument(..., help="Your website address, for example gateway-it.com"),
               port: int = typer.Option(443, help="Specify a port number for your website"),
               amber_days: int = typer.Option(30, help="Specify a number of days for an amber trigger"),
               json_output: bool = typer.Option(False, help="Use json output"),
               ):
    """
    Example: ./endpoint_checker check-site gateway-it.com [ --port 443 ]
    """

    if json_output:
        print(GiveInfo.single_site_json_output(site_address, port, amber_days))
    else:
        print(GiveInfo.single_site_table_output(site_address, port, amber_days))


@app.command()
def db_check(file: str = typer.Option("site_list.yaml", help="Your config file location"),
              json_output: bool = typer.Option(False, help="Use json output"),
              ):
    """
    Example: ./endpoint_checker db-check [ --file site_list.yaml ]
    """
    if json_output:
        print(GiveInfo.yaml_json_output(file))
    else:
        print(GiveInfo.yaml_table_output(file))


@app.command()
def db_add(file:str = typer.Option("site_list.yaml", help="Your config file location"),
                site_name:str = typer.Argument(..., help="Website address or domain, ie gateway-it.com"),
                site_port:int = typer.Option(443, help="SSL port used by the website"),
                site_owner:str = typer.Option("", help="Specify site owner"),
                amber_days:int = typer.Option(30, help="Days to mark site as \"amber\""),
                description:str = typer.Option("", help="Site description"),
            ):
    """
    Example: ./endpoint_checker db-add gateway-it.com [ --file site_list.yaml --site-owner \"Yaroslav Koisa\"]
    """

    if not os.path.exists(file):
        with open(file, 'w') as _file:
            pass

    new_ws_dict = {}
    new_ws_dict["site_name"] = site_name
    new_ws_dict["site_port"] = site_port
    new_ws_dict["amber_days"] = amber_days
    if site_owner:
        new_ws_dict["site_owner"] = site_owner
    if description:
        new_ws_dict["description"] = description

    yaml_dict = ReadWriteYaml(yaml_file_location=file).website_list

    for site_number in range(0, len(yaml_dict)):
        site_name_in_db = str(yaml_dict[site_number]["site_name"])
        site_name_specified = "^" + site_name + "$"
        if re.match(site_name_specified, site_name_in_db):
            print("This site already exists in our database!")
            sys.exit(1)
        
        elif site_number == len(yaml_dict) -1:
            yaml_dict.append(new_ws_dict)
            yaml_dict_to_write = {}
            yaml_dict_to_write["websites"] = yaml_dict
            ReadWriteYaml(yaml_file_location=file, yaml_input_dict=yaml_dict_to_write).write()
            print("The site " + site_name + " was added to the database.")
            break


@app.command()
def db_remove(
                file: str = typer.Option("site_list.yaml", help="Your config file location"),
                site_name:str = typer.Argument(..., help="Website address or domain, ie gateway-it.com"),
                ):
    """
    Example: ./endpoint_checker db-remove gateway-it.com [ --file site_list.yaml ]
    """

    yaml_dict = ReadWriteYaml(yaml_file_location=file).website_list

    if len(yaml_dict) == 0:
        print("The database is empty! Nothing could be removed.")
        sys.exit(0)

    for site_number in range(0, len(yaml_dict)):
        site_name_in_db = str(yaml_dict[site_number]["site_name"])
        site_name_specified = "^" + site_name + "$"
        if re.match(site_name_specified, site_name_in_db):
            del yaml_dict[site_number]
            yaml_dict_to_write = {}
            yaml_dict_to_write["websites"] = yaml_dict
            ReadWriteYaml(yaml_file_location=file, yaml_input_dict=yaml_dict_to_write).write()
            print("The site " + site_name + " was removed from the database!")
            break
        
        elif site_number == len(yaml_dict) -1:
            print("The site " + site_name + " could not be found in our database!")
            sys.exit(1)




""" If this file is executed from the command line, activate Typer """

if __name__ == "__main__":
    app()
