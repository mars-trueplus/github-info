# -*- coding: utf-8 -*-

import retrieve_info
import requests
from fabric import Connection
import os

LOCAL_USER = 'xmars'
REPO_PATH = '/home/xmars/Documents/magestore-repo'
BITBUCKET_ROOT_API = 'https://api.bitbucket.org'
BITBUCKET_TOKEN = ''
BITBUCKET_USER = ''
LOCAL_CON = Connection('localhost')


def get_list_repo_url():
    clone_urls = []
    repos = retrieve_info.get_list_repos()

    for repo in repos:
        clone_urls.append(repo.get('clone_url'))
    return clone_urls


def export_home_command():
    return 'export HOME=/home/{user};'.format(user=LOCAL_USER)


def set_git_credential_command(credential_file_name):
    git_credential_url = os.path.abspath(credential_file_name)
    set_credential_command = "git config --global credential.helper 'store --file %s'" % git_credential_url
    LOCAL_CON.local(export_home_command() + set_credential_command)


def remove_git_credential():
    LOCAL_CON.local(export_home_command() + "git config --global --unset credential.helper")


def clone_repos():
    """
    clone github repos to local folder
    :return:
    """
    if not os.path.isdir(REPO_PATH):
        LOCAL_CON.local('mkdir -p %s' % REPO_PATH)

    clone_urls = get_list_repo_url()

    set_git_credential_command('github_credential_url')

    for url in clone_urls:
        repo_name = url.split('/')[-1].replace('.git', '')
        repo_path = '{path}/{repo_name}'.format(path=REPO_PATH, repo_name=repo_name)
        if os.path.isdir(repo_path):
            LOCAL_CON.local('rm -rf %s' % repo_path)
        # need export HOME to local .gitconfig file with credential
        clone_command = '{export_home} git clone {url} {repo_path}'.format(export_home=export_home_command(), url=url, repo_path=repo_path)
        try:
            LOCAL_CON.local(clone_command)
        except Exception as e:
            print(e)

    remove_git_credential()


def create_repo(repo_name):
    url = '/2.0/repositories/{username}/{repo_slug}'.format(username='mars-trueplus', repo_slug=repo_name)
    url += '?access_token=%s' % BITBUCKET_TOKEN
    api_url = BITBUCKET_ROOT_API + url
    resp = requests.post(api_url, {'is_private': True})
    if resp.status_code != 200:
        return False
    bitbucket_url = resp.json()['links']['clone'][0]['href']
    return bitbucket_url


def push_repo(repo_path, repo_url):
    """
    Push local repo to bitbucket
    :param repo_path:
    :param repo_url:
    :return:
    """
    init_repo_cmd = 'git init && git add --all && git commit -m "Magestore - Backup Github Repos"'
    set_remote_cmd = 'git remote add origin %s' % repo_url
    push_cmd = 'git push -u origin --all'
    LOCAL_CON.local('{export_home} cd {repo_path} && {init_repo_cmd} && {set_remote_cmd} && {push_cmd}'.format(
        export_home=export_home_command(),
        repo_path=repo_path,
        init_repo_cmd=init_repo_cmd,
        set_remote_cmd=set_remote_cmd,
        push_cmd=push_cmd)
    )


def push_repos():
    for d in os.listdir(REPO_PATH):
        path = os.path.abspath(d)


if __name__ == '__main__':
    # push_repos()
    clone_repos()
    # params_path = os.path.abspath('bitbucket_params')
    # bitbucket_params = retrieve_info.read_params(params_path)
    # BITBUCKET_TOKEN = bitbucket_params.get('ACCESS_TOKEN')
    # create_repo('aaaaaa-bla-blem')
