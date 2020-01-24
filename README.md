# AWS Cognito user data export

A Python script for exporting user data from an AWS Cognito user pool. It automates the tedium of fetching many users using the AWS CLI. User data is stored to a single JSON file, with the option to also produce a CSV summary.

## Setup

Python 3 and [docopt](https://github.com/docopt/docopt) are required. You can install docopt using PIP:

```bash
pip install docopt
```

The AWS CLI is used to communicate with AWS Cognito. This requires credentials to be set up in a `.aws/credentials` file in your home directory. See [AWS credential file settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) for more details.

## Usage

To export all users to a JSON file, simply pass the ID of the user pool:

```
cognito-export.py <user-pool-id>
```

Exported data is saved in the current working directory, with the user pool ID and a timestamp in the file name.

For a full list of options run `cognito-export.py --help`.
