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
parser.add_argument('-cp', '--clear-pending-queue', help='Clear all items in the pending scan queue.',
                    action='store_true')
parser.add_argument('-dr', '--delete-all-repositories', help='Delete all known image image repositories. Warning: this '
                                                             'action cannot be undone and all image data will be '
                                                             'deleted.', action='store_true')
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
    pages = query_pages(api_url, params={'page_size': 50}, headers=headers)
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


def output_sensitive_images(auth_token):

    images = get_images(base_url, auth_token)
    print("Images with Sensitive Data: ")
    print("------------------------------")
    for image in images:
        if image[2] > 0:
            print("Registry: " + image[0] + " | " + "Image: " + image[1] + " | " + "Sensitive Files: " + str(image[2]) +
                  " | " + "Disallowed: " + str(image[3]))


def get_pending_scan_queue(t_url, auth_token):
    api_url = t_url + "/api/v1/scanqueue"
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    params = {'statuses': 'pending', 'page_size': '50'}
    pages = query_pages(api_url, params=params, headers=headers)

    queue_items = list()
    for page in pages:
        for item in page['result']:
            queue_items.append(item)

    return queue_items


def clear_pending_scan_queue(auth_token):
    queue = get_pending_scan_queue(base_url, auth_token)
    api_url = base_url + "/api/v1/scanqueue/cancel_jobs"
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    response = requests.post(api_url, data='{"statuses":["pending"]}', headers=headers)
    if response.status_code != 200:
        print("Cancelled " + str(len(queue)) + " scan jobs.")
    else:
        print("Scan cancellation failed: " + response.text)


def get_repositories(t_url, auth_token):
    api_url = t_url + "/api/v2/repositories"
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    params = {'page_size': 50, 'include_totals': True, 'order_by': 'name'}
    pages = query_pages(api_url, params=params, headers=headers)
    repositories = list()
    for page in pages:
        for repo in page['result']:
            repositories.append(repo)
    return repositories

def delete_repositories(auth_token):
    del_count = 0
    repos = get_repositories(base_url, token)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    for repo in repos:
        registry_name = repo['registry']
        repo_name = repo['name']
        response = requests.delete(base_url + "/api/v2/repositories/" + registry_name + "/" + repo_name, headers=headers)
        if response.status_code != 202:
            print("Deletion of " + registry_name + "/" + repo_name + " failed: " + response.text)
        else:
            del_count += 1

    print("Deleted " + str(del_count) + " repositories.")

if __name__ == '__main__':
    token = perform_login()
    try:
        if args.show_sensitive_images:
            output_sensitive_images(token)
        elif args.clear_pending_queue:
            clear_pending_scan_queue(token)
        elif args.delete_all_repositories:
            delete_repositories(token)

    except KeyboardInterrupt:
        print("\nExiting by user request.\n", file=sys.stderr)
        sys.exit(0)
