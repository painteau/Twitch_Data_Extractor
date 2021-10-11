import time, glob, cv2, os, csv, sys, datetime, logging
from PIL import Image
from twitch import TwitchClient
from pathlib import Path
from logging.handlers import RotatingFileHandler
from statistics import median 
from config import * 
from currency_converter import CurrencyConverter


# VARIABLES AND CONSTANTS

path_dir = r'D:/TWITCH_DATA/all_revenues' # CSV Directory without ending slash !



#FUNCTIONS AND CLASSES

clear = lambda: os.system('cls')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)


print("--------------------")

# Retrieve ID channel

my_channel = input("What is the Username of the Channel : ")
client = TwitchClient(client_id, oauth_token)
users = client.users.translate_usernames_to_ids(my_channel)
#users = client.users.translate_usernames_to_ids(['lirik', 'giantwaffle'])
for user in users:
    #RESET DATA 
    data = {}
    total_revenue_overall = float(0)

    print("--------------------")
    print(f"Searching through databases for {user.name} (ID {user.id})...")
    # Extracting revenues from CSVs
    for source_name in glob.glob(path_dir + "/**/*.csv" ,  recursive = True):
        # path, fullname = os.path.split(source_name)
        csv_file = csv.reader(open(source_name, "r"), delimiter=",") # read csv, and split on "," the line
        for row in csv_file: #loop through the csv list
            #if current rows 1st value is equal to input, print that row
            if user.id == row[0]:
                #Date formatting
                date_time_str = row[11]
                date_time_obj = datetime.datetime.strptime(date_time_str, '%m/%d/%Y')
                date_formatted = date_time_obj.date()       
                total_revenue_gross = float(row[2]) + float(row[3]) + float(row[4]) + float(row[5]) + float(row[6]) + float(row[7]) + float(row[8]) + float(row[9]) + float(row[10])
                data[date_formatted] = round(c.convert(float(total_revenue_gross), 'USD', 'EUR', date=date_formatted), 2)
                print(f"Found total gross of {round(c.convert(float(total_revenue_gross), 'USD', 'EUR', date=date_formatted), 2)} € on {date_formatted}")
    print(f"Computing all data...")
    # Extracting data for this user
    tax_file = csv.reader(open('tax_withholding_rates.csv', "r"), delimiter=",")
    for row in tax_file:
          if user.id == row[0]:
                finance_category = row[1]
                live_payout_entity_id = row[2]
                royalty_withholding_rate = row[3]
                service_withholding_rate = row[4]
                royalty_rate_updated_at = row[5]
                service_rate_updated_at = row[6]
                attribution_updated_at = row[7]
                onboarded_at = row[8]
                moneypenny_category = row[9]
                date_time_str = row[7]
                date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%SZ')
                date_formatted = date_time_obj.date()  

    print("--------------------")
    print("----  RECAP  -------")
    print("--------------------")


    for key in data:
        total_revenue_overall = total_revenue_overall + float(data[key])

    median_monthly_revenue = round(median(data.values()),2)
    average_monthly_revenue = round(sum(data.values()) / len(data),2)

    fulldata = {}
    fulldata['username'] = user.name
    fulldata['user_id'] = user.id
    fulldata['finance_category'] = finance_category
    fulldata['attribution_date'] = date_formatted
    fulldata['royalty_withholding_rate'] = royalty_withholding_rate
    fulldata['total_revenue_overall'] = round(total_revenue_overall, 2)
    fulldata['median_monthly_revenu'] = median_monthly_revenue
    fulldata['average_monthly_revenue'] = average_monthly_revenue

    with open('data.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(fulldata)
        writer.writerows(data)