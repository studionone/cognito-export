#! /usr/bin/env python3

import subprocess
import json
import csv
from datetime import datetime

DATE_FORMAT = '%Y/%m/%d %H:%M:%S'

options = {
    'region': 'ap-southeast-2',
    'profile': 'parkify',
    'user-pool-id': '',
}

args = ['aws', 'cognito-idp', 'list-users']
for key, value in options.items():
    args += ['--' + key, value]

users = []
done = False
token = None

# Loop through all pages of API results
while not done:
    all_args = args + (['--pagination-token', token] if token is not None else [])
    result = subprocess.run(all_args, capture_output=True)
    data = json.loads(result.stdout.decode('utf-8'))

    if 'PaginationToken' in data:
        token = data['PaginationToken']
    else:
        done = True

    users += data['Users']

print('Found {} users'.format(len(users)))

# Reformat API data
for user in users:
    attributes = {item['Name']: item['Value'] for item in user['Attributes']}
    user['Attributes'] = attributes

# Export JSON
with open('./cognito-users.json', 'w') as f:
    json.dump(users, f, indent=4)

# Export CSV
with open('./cognito-users.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Created', 'Modified'])

    for user in users:
        writer.writerow([
            user['Attributes']['sub'],
            '{} {}'.format(user['Attributes'].get('given_name', ''),
                           user['Attributes'].get('family_name', '')),
            user['Attributes'].get('email', ''),
            user['Attributes'].get('phone_number', ''),
            datetime.utcfromtimestamp(user['UserCreateDate']).strftime(DATE_FORMAT),
            datetime.utcfromtimestamp(user['UserLastModifiedDate']).strftime(DATE_FORMAT),
        ])
