# -*- coding: utf-8 -*-

import requests

API_URL_ROOT = 'https://api.github.com'
API_USER = ''
API_TOKEN = ''


def read_params(filename):
    vals = {}
    lines = open(filename, 'r').readlines()
    for line in lines:
        data = line.split('=')
        if len(data) == 2:
            data = ["".join(x.split()) for x in data]
            vals[data[0]] = data[1]
    return vals


def get_git_credential():
    vals = read_params('git_credential')
    user = vals.get('USER')
    token = vals.get('TOKEN')
    return user, token


def generate_api_request_url(api_url):
    url = API_URL_ROOT + api_url
    url = url.replace('USER', API_USER)
    url += '?access_token=%s' % API_TOKEN
    return url


def get_api_response_data(api_url):
    url = generate_api_request_url(api_url)
    resp = requests.get(url)
    data = resp.json()
    return data


def get_list_repos():
    api_url = '/user/repos'
    repos = get_api_response_data(api_url)
    with open('repos.csv', 'w') as f:
        f.write('#, Repo, Type, Team, Owner, Description\n')
        for index, repo in enumerate(repos):
            name = repo.get('name')
            type = 'Private' if repo.get('private') else 'Public'
            owner = repo.get('owner').get('login')
            teams = get_list_team_by_repo(name, owner)
            # FIXME: get list of team name

            description = repo.get('description')
            f.write('%s ,%s ,%s ,%s , %s, %s\n' % (index, name, type, '', owner, description))


def get_list_team_by_repo(repo_name, owner_name):
    api_url = '/repos/{owner_name}/{repo_name}/teams'.format(owner_name=owner_name, repo_name=repo_name)
    data = get_api_response_data(api_url)
    return data

#
# def test_repos():
#     api_url = '/user/repos'
#     repos = get_api_response_data(api_url)
#     with open('repos.csv', 'w') as f:
#         f.write('#, Repo, Type, Team, Owner, Description\n')
#         for index, repo in enumerate(repos):
#             name = repo.get('name')


if __name__ == '__main__':
    API_USER, API_TOKEN = get_git_credential()
    get_list_repos()
