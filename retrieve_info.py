# -*- coding: utf-8 -*-

import requests

API_URL_ROOT = 'https://api.github.com'
API_USER = ''
API_TOKEN = ''
TEAM_PERMISSION = {'pull': 'Read', 'push': 'Write', 'admin': 'Admin'}


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


def generate_api_request_url(api_url, params=None):
    url = API_URL_ROOT + api_url
    url = url.replace('USER', API_USER)
    params_str = ''
    if not params:
        params = {}
    params.update({
        'access_token': API_TOKEN
    })
    for i, key in enumerate(sorted(list(params.keys()))):
        if i == 0:
            seperator = '?'
        else:
            seperator = '&'
        params_str += "%s%s=%s" % (seperator, key, params.get(key))
    url += params_str
    return url


def get_api_response_data(api_url, params=None):
    url = generate_api_request_url(api_url, params)
    resp = requests.get(url, params)
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data


def get_list_repos():
    api_url = '/orgs/Magestore/repos'
    page = 1
    repos = []
    per_page = 100

    repo_info = []
    descriptions = []

    while True:
        res = get_api_response_data(api_url, {'page': page, 'per_page': per_page})
        if not res:
            break
        repos += res
        page += 1

    repo_info.append('#, Repo, Type, Team, Team permission, Owner, Description\n')
    for ip, repo in enumerate(repos):
        name = repo.get('name')
        repo_type = 'Private' if repo.get('private') else 'Public'
        owner = repo.get('owner').get('login')
        description = repo.get('description') or ''

        teams = get_list_team_by_repo(name, owner)
        if not teams:
            repo_info.append('%s ,%s ,%s ,%s , %s, %s, %s\n' % (ip + 1, name, repo_type, '', '', owner, ''))
            descriptions.append(description)
        else:
            for it, team in enumerate(teams):
                if it == 0:
                    repo_info.append('%s ,%s ,%s ,%s , %s, %s, %s\n' % (ip + 1, name, repo_type, team.get('name'), TEAM_PERMISSION.get(team.get('permission')), owner, ''))
                    descriptions.append(description)
                else:
                    repo_info.append('%s ,%s ,%s ,%s , %s, %s, %s\n' % ('', '', '', team.get('name'), TEAM_PERMISSION.get(team.get('permission')), '', ''))
                    descriptions.append(' ')

    with open('repos.csv', 'w') as f:
        for info in repo_info:
            f.write(info)

    with open('description.csv', 'w') as f:
        f.write('Desc')
        for des in descriptions:
            f.write(des + '\n')


def get_list_team_by_repo(repo_name, owner_name):
    api_url = '/repos/{owner_name}/{repo_name}/teams'.format(owner_name=owner_name, repo_name=repo_name)
    teams = get_api_response_data(api_url)
    return teams


if __name__ == '__main__':
    API_USER, API_TOKEN = get_git_credential()
    get_list_repos()
