"""
Python3 program that demonstrates how to add an attachment to a request using the iLab API.

Requires the installation of the "requests" python library. pip install requests.
You should update API_BASE below to your server.
Requires an environment variable, defined below, that contains your API Bearer Token; update to work with your secrets.

Joe Gregoria, University of Michigan Advanced Genomics Core. Feb 2023.

To run:
export ILAB_API_TOKEN="NONYA-BIZZNESS"
python3 main.py -id 123456 -f ~/readme.txt -n "A Test Attachment" -v
"""

import argparse
import os
from pprint import pprint

# pip install requests
import requests as requests

###
# You may want to customize these for your iLab settings.
API_BASE = "https://api.ilabsolutions.com/v1/"

API_TOKEN_ENVIRONMENT_VARIABLE = 'ILAB_API_TOKEN'
if not os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE):
    raise RuntimeError("This program requires an environment variable named {API_TOKEN_ENVIRONMENT_VARIABLE}")
AUTHORIZATION_TOKEN = f"bearer {os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)}"
#
###


def upload_attachment(ilab_request_id, filename, note=None):
    """
    Use the new (Feb 2023) iLab API to upload an attachment to an iLab request.
    :param ilab_request_id: The request ID from iLab.
    :param filename: Path to the file to upload.
    :param note: A string that appears under the file in the iLab UI.
    It is called "name" in the API and implies it's the file name, but the UI calls it "note"
    :return: the request from iLab as JSON
    """

    if not os.path.isfile(filename):
        raise FileNotFoundError(f"file not found: {os.path.abspath(filename)}")

    url = f"{API_BASE}attachments?object_class=ServiceItem&id={ilab_request_id}"

    post_files = {'attachment[uploaded_data]': open(filename, 'rb')}
    if note:
        post_data = {'attachment[name]': note}
    else:
        post_data = None

    try:
        headers = {'Authorization': AUTHORIZATION_TOKEN}
        response = requests.post(url, headers=headers, files=post_files, data=post_data)
    except Exception as ex:
        print(f"Failure sending attachment for {ilab_request_id} to iLab: {filename}")
        print(ex)
        raise

    if response.status_code != 200:
        # if you get a 401 response, almost for sure you don't have the right api bearer token.
        # if you get a 403 response, almost for sure you don't have access to the iLab request id.
        print(f"{response} sending attachment for request id {ilab_request_id} to iLab: {filename}")
        print(f"response.request.url: {response.request.url}")
        # print(f"response.request.headers: {response.request.headers}")   # WARNING! This could expose your secret bearer token
        print(f"response.request.body: {response.request.body}")
        print(f"response.status_code: {response.status_code}")
        print(f"response.headers: {response.headers}")
        raise RuntimeError(f"HTTP {response} error sending attachment for request id {ilab_request_id} to iLab: {filename}")

    return response.json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add an attachment (file) to an iLab request')
    parser.add_argument('-id', '--ilab_request_id', required=True, type=str, help='The (internal) iLab id of the request.')
    parser.add_argument('-f', '--filename', required=True, type=str, help='The path to the file to attach to the reqeust.')
    parser.add_argument('-n', '--note', required=False, type=str, help='Optional. A note or friendly name of the attachment.')
    parser.add_argument('-v', '--verbose', required=False, action='store_true', help="Optional. Turn on verbose mode.")
    args = parser.parse_args()

    updated_request = upload_attachment(ilab_request_id=args.ilab_request_id, filename=args.filename, note=args.note)

    if args.verbose:
        pprint(updated_request)
    else:
        print('Done.')
