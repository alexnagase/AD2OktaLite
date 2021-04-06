# AD2OktaLite
Autogenerate Okta Group rules for transfering AD Master to Okta Master. Based on ad_to_okta:
https://github.com/delize/ad_to_okta/blob/master/ad-to-okta-migration.py

## About
This script assists with the migration of Active Directory Mastered Okta group to an Okta Mastered Okta group. While ad_to_okta scans the entire Okta environment and then transfers all AD groups, you can pick and choose an individual target AD group with this one. You will need an Org Admin or higher Okta Token, Org Okta URL, and Python 3

## Instructions
1. Identify the Active Directory Mastered Okta group you want to transfer.
2. Run the Python File with your Okta environment info as arguments. 
3. Follow steps from the program
4. Enable the generated rule in the Okta admin console. Optionally disable/remove rule when completed. 

