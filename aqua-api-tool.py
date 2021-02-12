import requests
import json
import argparse
from urllib3 import disable_warnings, exceptions
import sys

disable_warnings(exceptions.InsecureRequestWarning)
parser = argparse.ArgumentParser(description='Aqua Security tool for interacting with Aqua Enterprise API.')
parser.add_argument('-u', '--user', help='Username or service account for logging into Aqua.', required=True)
parser.add_argument('-p', '--password', help='Password for logging into Aqua.', required=True)
parser.add_argument('-U', '--url', help='Aqua base URL. (ie. https://aqua.company.com)', required=True)
parser.add_argument('-s', '--show-sensitive-images', help='Return all known images that contain sensitive data.',
                    action='store_true')
args = parser.parse_args()

base_url = args.url
username = args.user
password = args.password


def perform_login():
    url = base_url + "/api/v1/login"
    payload = {'id': username, 'password': password, 'remember': True}
    headers = {'Content-Type': 'application/json'}

    payload = json.dumps(payload)
    response = requests.post(url, data=payload, headers=headers, verify=False)

    if response.status_code != 200:
        resp = json.loads(response.text)
        sys.exit(resp['message'])

    response_json = response.json()
    token = response_json["token"]

    return token


def get_images(url, auth_token):
    api_url = url + "/api/v2/images"
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    pages = query_pages(api_url, params={}, headers=headers)
    images = []
    for page in pages:
        for name in page['result']:
            images.append([name['registry'], name['name'], name['sensitive_data'], name['disallowed']])
    return images


def query_pages(t_url, params, headers):
    addtl_pages = True
    page_cnt = 0
    page_set = []
    while addtl_pages:
        page_cnt += 1
        params['page'] = page_cnt
        res = requests.get(t_url, headers=headers, params=params, verify=False)
        json_result = res.json()
        if (json_result == [] or json_result['result'] == None) or len(json_result['result']) == 0:
            if res.status_code != 200:
                print('Failure: ' + res.reason)
            addtl_pages = False
            break
        page_set.append(json_result)
    return page_set


def output_sensitive_images():
    token = perform_login()

    images = get_images(base_url, token)
    print("Images with Sensitive Data: ")
    print("------------------------------")
    for image in images:
        if image[2] > 0:
            print("Registry: " + image[0] + " | " + "Image: " + image[1] + " | " + "Sensitive Files: " + str(image[2]) +
                  " | " + "Disallowed: " + str(image[3]))


if __name__ == '__main__':
    try:
        if args.show_sensitive_images:
            output_sensitive_images()
        # elif args.something:
        #     output_sensitive_images()
    except KeyboardInterrupt:
        print("\nExiting by user request.\n", file=sys.stderr)
        sys.exit(0)
