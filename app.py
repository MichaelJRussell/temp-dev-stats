import os
import re
import sys
import traceback
import logging
import argparse
import logging_config

from clients.github_client import GithubClient
from pymongo import MongoClient
from clients.jira_client import JiraClient
from models.github_pull import GithubPull

logger = logging.getLogger(__name__)
stdout_logger = logging.getLogger('stdout_logger')

re_story_num_title = re.compile(r"([a-zA-Z]{1,10}-\d{1,5}):?\s")
re_story_num_body = re.compile(r"atlassian\.net/browse/([a-zA-Z]{1,10}-\d{1,5})\)")

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument('--jira_username')
    parser.add_argument('--jira_token')
    parser.add_argument('--github_token')
    parser.add_argument('--repo')

    return parser

def get_jira_story_num(pr: GithubPull) -> str:
    jira_match = re_story_num_title.search(pr.title)

    if not jira_match:
        jira_match = re_story_num_body.search(pr.body)

    if jira_match:
        return jira_match.group(1)

    if not jira_match:
        logger.info(f'No matching Jira story for PR {pr}')

    return None


def main():
    parser = init_argparse()
    args = parser.parse_args()
    mongo_client = MongoClient(port=27017)
    cache_db = mongo_client['dev-cache']
    client = GithubClient(args.github_token, args.repo, cache_db)
    jira_client = JiraClient(args.jira_username, args.jira_token, cache_db)
    prs = client.get_prs()

    for pr in prs:
        jira_issue = get_jira_story_num(pr)

        if jira_issue:
            pass
            jira_client.get_issue(jira_issue)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(f'Unexpected error: {traceback.format_exc()}')
        logger.error(f'Unexpected error: {traceback.format_exc()}')
