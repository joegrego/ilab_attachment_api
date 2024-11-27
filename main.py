"""
Python3 program that demonstrates how to add an attachment to a request using the iLab API.

Requires the installation of the "requests" python library. pip install requests.
You should update API_BASE below to your server.
Requires an environment variable, defined below, that contains your API Bearer Token; update to work with your secrets.

If you want to upload by-name instead of by-id, you need both the name of the request and your Core ID number from iLab.
Your Core ID is probably 4 digits, and probably is not 1234!

Joe Gregoria, University of Michigan Advanced Genomics Core. Feb 2023.

To run:
export ILAB_API_TOKEN="NONYA-BIZZNESS"
python3 main.py -id 123456 -f ~/readme.txt -n "A Test Attachment" -v
python3 main.py -name 123-JRG -c 1234 -f ~/readme.txt -n "A Test Attachment" -v
"""

import argparse
import os
from pprint import pprint

# pip install requests
import requests

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

    with (open(filename, 'rb')) as file_handle:
        post_files = {'attachment[uploaded_data]': file_handle}
        if note:
            post_data = {'attachment[name]': note}
        else:
            post_data = None

        try:
            headers = {'Authorization': AUTHORIZATION_TOKEN}
            response = requests.post(url, headers=headers, files=post_files, data=post_data, timeout=30)
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


def get_ilab_id_from_request_name(request_name, core_id, from_date="2000-01-01"):
    """
    Get the iLab ID from a request name. Our request names are in the form "1234-ABC", but yours probably are not.
    Your Core ID is probably 4 digits, and probably is not 1234!

    :param request_name: The iLab request name.
    :type request_name: str
    :param core_id: Your iLab Core ID.
    :type core_id: str
    :param from_date: How far back to go. The API default is 2 years; you probably want more than that.
    :type from_date: str of ISO 8601 date. Like "2015-03-14"
    :return: The iLab id of that service request; Raises an error if something bad happens, including can't find the id.
    :rtype: str
    """
    if not request_name:
        raise ValueError("request_name required")
    if not core_id:
        raise ValueError("core_id required to get request by name")

    url = f"{API_BASE}cores/{core_id}/service_requests.json?name={request_name}&from_date={from_date}"

    try:
        headers = {'Authorization': AUTHORIZATION_TOKEN}
        response = requests.get(url, headers=headers, timeout=30)
    except Exception as ex:
        print(f"Failure getting ilab request for name  {request_name}")
        print(ex)
        raise

    if response.status_code != 200:
        # if you get a 401 response, almost for sure you don't have the right api bearer token.
        # if you get a 403 response, almost for sure you don't have access to the iLab request id.
        print(f"{response} getting iLab details for {request_name}")
        print(f"response.request.url: {response.request.url}")
        # print(f"response.request.headers: {response.request.headers}")   # WARNING! This could expose your secret bearer token
        print(f"response.request.body: {response.request.body}")
        print(f"response.status_code: {response.status_code}")
        print(f"response.headers: {response.headers}")
        raise RuntimeError(f"HTTP {response} error getting iLab request named {request_name}")

    # pprint(response.json())
    try:
        id = response.json()["ilab_response"]["service_requests"][0]["id"]
    except KeyError as ex:
        print(f"Failure getting iLab details for {request_name}: {ex}")
        raise

    return id


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add an attachment (file) to an iLab request')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-id', '--ilab_request_id', type=str, help='The (internal) iLab id of the request.')
    group.add_argument('-name', '--request_name', type=str, help='The iLab name of the request.')
    parser.add_argument('-f', '--filename', required=True, type=str, help='The path to the file to attach to the reqeust.')
    parser.add_argument('-n', '--note', required=False, type=str, help='Optional. A note or friendly name of the attachment.')
    parser.add_argument('-c', '--core_id', required=False, type=str, help='Optional. Your iLab Core ID number. Ours is 4 digits. '
                                                                          'Provide if you are using --request_name so we can get the request id.')
    parser.add_argument('-v', '--verbose', required=False, action='store_true', help="Optional. Turn on verbose mode.")
    args = parser.parse_args()

    if args.request_name:
        ilab_id = get_ilab_id_from_request_name(args.request_name, args.core_id)
        if args.verbose:
            print(f"iLab ID for {args.request_name}: {ilab_id}")
    elif args.ilab_request_id:
        ilab_id = args.ilab_request_id
    else:
        raise ValueError("Must specify either --ilab_request_id or --request_name")

    updated_request = upload_attachment(ilab_request_id=ilab_id, filename=args.filename, note=args.note)

    if args.verbose:
        pprint(updated_request)
    else:
        print(f'{os.path.abspath(args.filename)} uploaded to iLab request {ilab_id}.')
