#! /usr/bin/env python3

"""Cognito user data export

Usage: cognito-export.py [options] <user-pool-id>

Options:
  -h --help         Show this screen
  --profile <name>  The AWS credentials profile to use
  --csv             Export a CSV summary in addition to JSON data
"""

import subprocess
import json
import csv
from datetime import datetime
import os

from docopt import docopt

DATE_FORMAT = '%Y/%m/%d %H:%M:%S'


def pool_info(pool_id):
    """Split a user pool ID into region and ID"""
    return pool_id.split('_')


class CognitoExport:
    def __init__(self, pool_id, profile='default'):
        """Fetch all users using AWS CLI"""
        self.users = []

        options = {
            'region': pool_info(pool_id)[0],
            'profile': profile,
            'user-pool-id': pool_id,
        }

        args = ['aws', 'cognito-idp', 'list-users']
        for key, value in options.items():
            args += ['--' + key, value]

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

            self.users += [self.format(u) for u in data['Users']]

    def format(self, user):
        """Reformat API data for a single user"""
        attributes = {item['Name']: item['Value'] for item in user['Attributes']}
        user['Attributes'] = attributes
        return user

    def export_json(self, path):
        """Export all user data to a JSON file"""
        with open(path, 'w') as f:
            json.dump(self.users, f, indent=4)

    def export_csv(self, path):
        """Export default Cognito parameters to a CSV file"""
        with open(path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Created', 'Modified'])

            for user in self.users:
                writer.writerow([
                    user['Attributes']['sub'],
                    '{} {}'.format(user['Attributes'].get('given_name', ''),
                                   user['Attributes'].get('family_name', '')),
                    user['Attributes'].get('email', ''),
                    user['Attributes'].get('phone_number', ''),
                    datetime.utcfromtimestamp(user['UserCreateDate']).strftime(DATE_FORMAT),
                    datetime.utcfromtimestamp(user['UserLastModifiedDate']).strftime(DATE_FORMAT),
                ])


if __name__ == '__main__':
    args = docopt(__doc__)

    print('Fetching data...')
    data = CognitoExport(args['<user-pool-id>'], args['--profile'])

    filename = 'cognito-{}-{}'.format(pool_info(args['<user-pool-id>'])[1],
                                      datetime.now().strftime('%Y%m%d-%H%M'))

    # Export JSON
    data.export_json(os.path.join(filename + '.json'))

    # Export CSV
    if args['--csv']:
        data.export_csv(os.path.join(os.getcwd(), filename + '.csv'))

    print('Exported {} users'.format(len(data.users)))
