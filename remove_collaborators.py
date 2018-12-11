# -*- coding: utf-8 -*-

import requests
from retrieve_info import generate_api_request_url


def remove_user_as_collaborator(owner, repo, user):
    api = "/repos/{owner}/{repo}/collaborators/{user}"
    api = api.format(
        owner=owner,
        repo=repo,
        user=user
    )
    api_url = generate_api_request_url(api)
    resp = requests.delete(api_url)
    return resp


def remove_team_as_collaborator(team_id, owner, repo):
    api = "/teams/{team_id}/repos/{owner}/{repo}"
    api = api.format(
        team_id=team_id,
        owner=owner,
        repo=repo
    )
    api_url = generate_api_request_url(api)
    resp = requests.delete(api_url)
    return resp


if __name__ == '__main__':
    resp = remove_team_as_collaborator('886699', 'Microsoft', 'demo-remote-team-collaborator')
    print(resp.status_code)
