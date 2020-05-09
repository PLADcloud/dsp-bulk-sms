#! /usr/bin/python3

from twilio.rest import Client
from datetime import date
import csv
import sys


# Twilio API Key information (from Twilio console)
account_sid = 'AC8c99c08c498111a263c0861dd92d08b9'
APIKeySecret = '3AeYQ8yH7r76M0LSaHaYEnMGebrSVIXD'
APIKeySID = 'SK1c52dcb6652687cbd372b9b42b630d06'

# come constants for use in defining command line arguments and record separator for effort only
recordSep = "<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>\n"
DriverArg = '--drivers'
MessageArg = '--message'
MediaArg = '--mediaURL'
today = date.today().strftime("%m-%d-%Y")

# These are flags that control execution.  Generally over ridden by command line arguments
effortOnly = False
vanNotify = True
AddSMSHeader = True
standupMessage = False
MediaOnly = False
processFICO = False
messageFromFile = False
shiftMessage1 = ', you are confirmed as a driver for the 12:05 Wave on ' + today + '.\nReport directly to your assigned vehicle [#'
shiftMessage2 = '].\n(1) Perform eMentor check\n(2) Login to Flex\n(3) Arrive in the load out line by 11:55 AM\n'
mediaMessage = f"Please click on the link below to hear the standup message for {today}\n"
DriverListCSV = "Driver List Manager - Output Sheet.csv"

# Some variable we will be using later in the program
theMessage = ''
driverNumber = ''
SMSMessage = 'Undefined'

# Authenticate with Twilio - now we can use Client to access Twilio REST API
client = Client(APIKeySID, APIKeySecret, account_sid)

# Process command line arguments if this is the main program
if __name__ == "__main__":

    # Process command line arguments
    for i, arg in enumerate(sys.argv):
        if i == 0 or sys.argv[i-1].lower() in [DriverArg.lower(), MessageArg.lower(), MediaArg.lower()]:
            continue
        if arg.lower() == "--EffortOnly".lower():
            effortOnly = True
        elif arg.lower() == DriverArg.lower():
            DriverListCSV = sys.argv[i+1]
        elif arg.lower() == MessageArg.lower():
            messageFromFile = True
            with open(sys.argv[i+1], mode='r') as file:
                SMSMessage = file.read()
        elif arg.lower() == MediaArg.lower():
            MediaURL = sys.argv[i+1]
            standupMessage = True
        elif arg.lower() == '--MediaOnly'.lower():
            MediaOnly = True
        elif arg.lower() == '--noVan'.lower():
            vanNotify = False
        elif arg.lower() == '--fico'.lower():
            processFICO = True
        elif arg.lower() == '--Help'.lower():
            print(f"Usage: SendSMS {MessageArg} <Message File Name> --EffortOnly {DriverArg} <Driver CSV File Name> {MediaArg} <URL for Standup media file access>")
            exit()
        elif arg.lower() == "--NoHeader".lower():
            AddSMSHeader = False
        else:
            print(f"Invalid Argument #{i} - [{arg.lower()}]")
            print(f"Usage: SendSMS {MessageArg} <Message File Name> --EffortOnly {DriverArg} <Driver CSV File Name> {MediaArg} <URL for Standup media file access>")
            exit()

with open(DriverListCSV) as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if messageFromFile == False:
            if vanNotify == True:
                theMessage = f"{row['Name']}{shiftMessage1}{row['Van #']}"
                if processFICO == True:
                    theMessage += f" FICO Score:{row['FICO']}{shiftMessage2}"
                else:
                    theMessage += shiftMessage2                
            else:
                theMessage = row["Name"] + shiftMessage1
                if processFICO == True:
                    theMessage += f" FICO Score:{row['FICO']}{shiftMessage2}"
                else:
                    theMessage += shiftMessage2
        else:
            if AddSMSHeader == True:
                theMessage = f"{today}: {row['Name']}"
                if vanNotify == True:
                    theMessage += f" Van: {row['Van #']}"
                if processFICO == True:
                    theMessage += f" FICO Score:{row['FICO']}\n"
                else:
                    theMessage += f"\n"
            theMessage += SMSMessage

        driverNumber = '+1' + row["Mobile #"]
        line_count += 1

        if effortOnly == True:
            print(recordSep)
            print(f"These SMS Messages would be sent to {row['Name']} -- {driverNumber}\n")

            if MediaOnly == False:
                 print(theMessage)

            if standupMessage == True:
                print("\nThis Media Message would be sent:\n")
                print(mediaMessage + MediaURL)

            print(recordSep)
            
        else:
            print(f'Message sent to {row["Name"]}')

            if MediaOnly == False:
                message = client.messages.create(
                    body=theMessage,
                    from_='+17038441584',
                    to=driverNumber
                )   
            
            if standupMessage == True:
                message = client.messages.create(
                    body = mediaMessage + MediaURL,
                    from_='+17038441584',
                    to = driverNumber
                )
        
    print('Processed', line_count, 'lines.')