#!/bin/python3
#AD to Okta Lite
#Based on AD to Okta by Andrew Doering

import argparse
import requests
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process user input for Active Directory to Okta transition")
    parser.add_argument('-u', '--url', type=str,
                        default='company.okta.com',
                        help='Replace company with the name of your org')
    parser.add_argument('-t', '--token', type=str,
                        default='You did not submit a token',
                        help='API Token from Okta instance')
    args = parser.parse_args()
    return (args.url, args.token)

def request_get(url, **kwargs):
    response = requests.get(url, params=kwargs, headers=HEADERS)
    response_data = response.json()
    while response.links.get('next'):
        links = response.links['next']['url']
        response = requests.get(links, headers=HEADERS)
        response_data += response.json()
    return response_data
    # while response:
    #     yield page
    #     page = get_next_page(page.links)

def get_okta_groups(url, **kwargs):
    url = f'https://{url}/api/v1/groups'
    return request_get(url, **kwargs)

def return_groups(app_filter):
    """Searches the groups pulled by the get_groups function, returns names"""
    groups = ""
    if app_filter == 'APP_GROUP' or app_filter == 'OKTA_GROUP':
        groups = get_okta_groups(url, filter='type eq "' + app_filter + '"')
        # print(groups)
    else:
        print("Not a valid group filter, must be APP_GROUP or OKTA_GROUP.")
    return groups

def return_ad_group_attributes():
    ad_groups = return_groups("APP_GROUP")
    if len(ad_groups) == 0:
        print('0 groups found.')
        return
    found_groups_attributes, found_groups_id, found_groups_desc, found_groups_name = ([] for i in range(4))
    for group in ad_groups:
        if 'windowsDomainQualifiedName' in group['profile']:
            found_groups_id.append(group['id'])
        if 'windowsDomainQualifiedName' in group['profile']:
            found_groups_name.append(group['profile']['name'])
        if 'windowsDomainQualifiedName' in group['profile']:
            found_groups_desc.append(group['profile']['description'])
    found_groups_attributes = list(zip(found_groups_name, found_groups_desc, found_groups_id))
    return found_groups_attributes

def return_okta_group_attributes():
    okta_groups = return_groups("OKTA_GROUP")
    if len(okta_groups) == 0:
        print('0 groups found.')
        return
    found_groups_attributes, found_groups_id, found_groups_desc, found_groups_name = (
        [] for i in range(4))
    for group in okta_groups:
        found_groups_id.append(group['id'])
        found_groups_name.append(group['profile']['name'])
        found_groups_desc.append(group['profile']['description'])
    found_groups_attributes = list(
        zip(found_groups_name, found_groups_desc, found_groups_id))
    return found_groups_attributes

def search_for_ad_group(search):
    ad_groups_list = return_ad_group_attributes()

    found = False
    for i, j ,k in ad_groups_list:
        if search == i:
            print("AD Mastered Group Name:" + str(i), "with ID:" + str(k))
            found = True
            return [i,j,k]
            break
    if not found:
        print("A match was not found. Exiting")
        sys.exit(0)

def search_for_okta_group(search):
    okta_groups_list = return_okta_group_attributes()

    found = False
    for i, j ,k in okta_groups_list:
        if search == i:
            print("Okta Group Name:" + str(i), "with ID:" + str(k))
            found = True
            return [i,j,k]
            break
    if not found:
        print("A match was not found. Exiting")
        sys.exit(0)

def create_okta_groups(group_name, group_desc):
    group_info = return_ad_group_attributes()

    group = {"profile": {"name": group_name,
                         "description": "AD2OKTALite-API - " + group_desc}}
    status = requests.post(f"https://{url}/api/v1/groups",
                           json=group, headers=HEADERS)
    if status.status_code == 200:
        print(f"Group {group_name} created. Success!")
    elif status.status_code == 400:
        print(f"Group {group_name} already exists. Continuing to Group Rules.")
    elif status.status_code == 401:
        print('Not Authorized.')
        sys.exit(0)
    elif status.status_code == 404:
        print('Not Found.')
        sys.exit(0)
    else:
        print('Something fucked up!')
        sys.exit(0)
    return status

def create_group_rules(group_name,oldgroupid,newgroupid):

    rule_name = "API-AD2OL" + " " + group_name
    group_rule = group_rule = {
        'type': 'group_rule',
        'name': rule_name,
        'conditions': {
            'expression': {
                'value': f"isMemberOfAnyGroup('{oldgroupid}')",
                'type': 'urn:okta:expression:1.0'
            }
        },
        'actions': {
            'assignUserToGroups': {
                'groupIds': [
                    newgroupid
                ]
            }
        }
    }
    status = requests.post(f"https://{url}/api/v1/groups/rules/",
                           json=group_rule, headers=HEADERS)
    if status.status_code == 200:
        print(f"Group rule for {group_name} created. Success!")
    elif status.status_code == 400:
        print('Bad Request.')
    elif status.status_code == 401:
        print('Not Authorized.')
    elif status.status_code == 404:
        print('Not Found.')
    else:
        print(requests.content)
        print('Something fucked up!')
    return status

if __name__ == '__main__':
    (url, token,) = parse_args()

    HEADERS = {
        'Authorization': 'SSWS ' + token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    while True:
        ADGroupName = input("Enter AD Group Name: ")
        ADGroupList = search_for_ad_group(ADGroupName)
        if input('Do You Want To Generate Okta Group? y or n: ') == 'y':
            break

    create_okta_groups(ADGroupList[0],ADGroupList[1])
    create_group_rules(ADGroupList[0],ADGroupList[2],search_for_okta_group(ADGroupList[0])[2])
    print('Rule is disabled by default. Enable in Admin Console')






