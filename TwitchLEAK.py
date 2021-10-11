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
    print('{}: {}'.format(user.name, user.id))



    # LOGGER SETUP

    # création de l'objet logger qui va nous servir à écrire dans les logs
    logger = logging.getLogger()
    # on met le niveau du logger à DEBUG, comme ça il écrit tout
    logger.setLevel(logging.DEBUG)
     # création d'un formateur qui va ajouter le temps, le niveau
    # de chaque message quand on écrira un message dans le log
    formatter = logging.Formatter('%(message)s')
    # création d'un handler qui va rediriger une écriture du log vers
    # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
    file_handler = RotatingFileHandler(f'log/{user.name}.log', 'a', 1000000, 1)
    # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
    # créé précédement et on ajoute ce handler au logger
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # création d'un second handler qui va rediriger chaque écriture de log
    # sur la console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    #logging.debug('This message should not go to the log file')
    #logging.info('but should this')
    #logging.warning('And this, too')

    clear()

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
                #print (f"Details for {bcolors.OKGREEN}{bcolors.BOLD}{user.name}{bcolors.ENDC}{bcolors.ENDC} (User ID : {user.id} )")
                #print(f'Date: {date_time_obj.date()})
                print(f"Found total gross of {round(c.convert(float(total_revenue_gross), 'USD', 'EUR', date=date_formatted), 2)} € on {date_formatted}")

                #print (f"---------")
                #print (f"Details :")
                #print (f"payout_entity_id : {row[1]}")
                #print (f"ad_share_gross : {row[2]} $")
                #print (f"sub_share_gross : {row[3]} $")
                #print (f"bits_share_gross : {row[4]} $")
                #print (f"bits_developer_share_gross : {row[5]} $")
                #print (f"bits_extension_share_gross : {row[6]} $")
                #print (f"prime_sub_share_gross : {row[7]} $")
                #print (f"bit_share_ad_gross : {row[8]} $")
                #print (f"fuel_rev_gross : {row[9]} $")
                #print (f"bb_rev_gross : {row[10]} $")
                #print (f"experimental_rev_gross : {row[12]} $")

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
    logging.info(f'{user.name} has the {finance_category} status, since {date_formatted}, with a royalty rate of {royalty_withholding_rate}')
    logging.info("----  RECAP  -------")
    # Final PRINTING

    for key in data:
        total_revenue_overall = total_revenue_overall + float(data[key])
        logging.info(f'{key} -> {data[key]} €')

    logging.info("----  TOTAL  -------")
    logging.info(f'Total overall on all periods : {round(total_revenue_overall, 2)} €')

    median_monthly_revenue = round(median(data.values()),2)
    average_monthly_revenue = round(sum(data.values()) / len(data),2)
    # printing result average 
    logging.info(f"With an median revenue of  : {str(median_monthly_revenue)} € / month") 
    logging.info(f"and an average revenue of  : {str(average_monthly_revenue)} € / month") 