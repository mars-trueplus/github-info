# -*- coding: utf-8 -*-

import retrieve_info
import requests
from fabric import Connection
import os
from invoke.exceptions import UnexpectedExit
from slugify import slugify

LOCAL_USER = 'xmars'
REPO_PATH = '/home/xmars/Documents/magestore-repo'
BITBUCKET_ROOT_API = 'https://api.bitbucket.org'
BITBUCKET_TOKEN = ''
BITBUCKET_USER = ''
LOCAL_CON = Connection('localhost')


def update_bitbucket_params():
    global BITBUCKET_TOKEN, BITBUCKET_USER
    params = retrieve_info.read_params('bitbucket_params')
    BITBUCKET_TOKEN = params.get('ACCESS_TOKEN')
    BITBUCKET_USER = params.get('USER')


def get_list_repo_url():
    clone_urls = []
    repos = retrieve_info.get_list_repos()

    for repo in repos:
        clone_urls.append(repo.get('clone_url'))
    return clone_urls


def export_home_command():
    return 'export HOME=/home/{user};'.format(user=LOCAL_USER)


def set_git_credential(credential_file_name):
    git_credential_url = os.path.abspath(credential_file_name)
    set_credential_command = "git config --global credential.helper 'store --file %s'" % git_credential_url
    LOCAL_CON.local(export_home_command() + set_credential_command)


def remove_git_credential():
    try:
        LOCAL_CON.local(export_home_command() + "git config --global --remove-section credential")
    except (UnexpectedExit, Exception) as e:
        print(e)


def clone_repos():
    """
    clone github repos to local folder
    :return:
    """
    if not os.path.isdir(REPO_PATH):
        LOCAL_CON.local('mkdir -p %s' % REPO_PATH)

    clone_urls = get_list_repo_url()

    remove_git_credential()
    set_git_credential('github_credential_url.ms')

    for url in clone_urls:
        repo_name = url.split('/')[-1].replace('.git', '')
        repo_path = '{path}/{repo_name}'.format(path=REPO_PATH, repo_name=repo_name)
        bash_file = os.path.abspath('pull_all_branch.sh')
        if os.path.isdir(repo_path):
            LOCAL_CON.local('rm -rf %s' % repo_path)
        # need export HOME to local .gitconfig file with credential
        clone_command = '{export_home} git clone {url} {repo_path}'.format(export_home=export_home_command(), url=url, repo_path=repo_path)
        get_all_branch = '{export_home} cd {repo_path} && bash {bash_file}'.format(
            export_home=export_home_command(),
            repo_path=repo_path,
            bash_file=bash_file
        )
        try:
            LOCAL_CON.local(clone_command)
            LOCAL_CON.local(get_all_branch)
        except Exception as e:
            print(e)

    remove_git_credential()


def create_repo(repo_name):
    """
    Bitbucket slug: https://confluence.atlassian.com/bitbucket/what-is-a-slug-224395839.html
    :param repo_name:
    :return:
    """
    url = '/2.0/repositories/{username}/{repo_slug}'.format(username='mars-trueplus', repo_slug=slugify(repo_name))
    url += '?access_token=%s' % BITBUCKET_TOKEN
    api_url = BITBUCKET_ROOT_API + url
    resp = requests.post(api_url, {'name': repo_name, 'is_private': True})
    if resp.status_code != 200:
        return False
    clone_link = resp.json()['links']['clone']
    bitbucket_url = clone_link[0]['href'] if clone_link[0]['href'] == 'ssh' else clone_link[1]['href']
    return bitbucket_url


def push_repo(repo_path, repo_url):
    """
    Push local repo to bitbucket
    :param repo_path:
    :param repo_url:
    :return:
    """
    rm_old_git_cmd = 'rm -rf {repo_path}/.git'.format(repo_path=repo_path)
    set_remote_cmd = 'git remote set-url origin %s' % repo_url
    push_cmd = 'git push -u origin --all'
    LOCAL_CON.local(rm_old_git_cmd)

    try:
        LOCAL_CON.local('{export_home} cd {repo_path} && {set_remote_cmd} && {push_cmd}'.format(
            export_home=export_home_command(),
            repo_path=repo_path,
            set_remote_cmd=set_remote_cmd,
            push_cmd=push_cmd)
        )
    except UnexpectedExit as e:
        print(e)


def push_repos():
    remove_git_credential()
    set_git_credential('bitbucket_credential_url')
    for d in os.listdir(REPO_PATH):
        repo_path = REPO_PATH + '/' + d
        repo_url = create_repo(repo_name=d)
        if not repo_url:
            continue
        push_repo(repo_path, repo_url)


if __name__ == '__main__':
    clone_repos()
