import typing
import requests
import json
import logging
import uuid
from pymongo import database
from models.github_file import GithubFile
from models.github_comment import GithubComment
from models.github_pull import GithubPull

logger = logging.getLogger(__name__)

PULLS_URL = 'https://api.github.com/repos/globalvetlink/{0}/pulls/{1}'
PULL_LIST_URL = 'https://api.github.com/repos/globalvetlink/{0}/pulls?per_page=50&page={1}'
COMMENTS_URL = 'https://api.github.com/repos/globalvetlink/{0}/issues/{1}/comments'
REVIEWS_URL = 'https://api.github.com/repos/globalvetlink/{0}/pulls/{1}/reviews'
REVIEW_COMMENTS_URL = 'https://api.github.com/repos/globalvetlink/{0}/pulls/{1}/reviews/{2}/comments'
FILES_URL = 'https://api.github.com/repos/globalvetlink/{0}/pulls/{1}/files'
ISSUE_URL = 'https://api.github.com/repos/globalvetlink/{0}/issues/{1}'
TIMELINE_URL = 'https://api.github.com/repos/globalvetlink/{0}/issues/{1}/timeline'

class GithubClient:
    headers = { 'Authorization': '', 'Accept': 'application/vnd.github.v3+json' }
    headers_diff = { 'Authorization': '', 'Accept': 'application/vnd.github.v3.diff' }
    repo: str
    cache_db: database.Database

    def __init__(self, token: str, repo: str, cache_db: database.Database) -> None:
        self.repo = repo
        self.cache_db = cache_db

        self.headers['Authorization'] = f'token {token}'
        self.headers_diff['Authorization'] = f'token {token}'

    def cache_add_or_update(self, doc: typing.Dict, collection: str):
        if 'id' in doc.keys():
            query = {"repo_name": self.repo, "id": doc["id"]}
        else:
            query = {"repo_name": self.repo, "sha": doc["sha"]}

        doc['repo_name'] = self.repo

        self.cache_db[collection].replace_one(query, doc, True)

    def add_to_cache(self, data, collection: str):
        if not self.cache_db:
            return

        if isinstance(data, list):
            for doc in data:
                self.cache_add_or_update(doc, collection)
        else:
            self.cache_add_or_update(data, collection)

    def get_timeline(self, issue_num):
        url = TIMELINE_URL.format(self.repo, issue_num)
        response = requests.get(url, headers=self.headers)

        if not response.status_code == 200:
            logger.info(f'Timeline {issue_num}: Response status {response.status_code}')
            return None

        body = json.loads(response.text)
        doc = { 'id': f'{self.repo}-{issue_num}', 'issue_number': issue_num, 'events': body }

        self.add_to_cache(doc, 'timelines')

    def get_pr(self, pr_num) -> GithubPull:
        url = PULLS_URL.format(self.repo, pr_num)
        response = requests.get(url, headers=self.headers)

        if not response.status_code == 200:
            logger.info(f'PR {pr_num}: Response status {response.status_code}')
            return None

        body = json.loads(response.text)

        self.add_to_cache(body, 'pulls')

        return GithubPull(body)

    def get_prs(self) -> typing.List[GithubPull]:
        max_pages = 5 # sanity check to restrict number of requests
        page = 0
        prs = []

        while page < max_pages:
            page += 1

            url = PULL_LIST_URL.format(self.repo, page)
            response = requests.get(url, headers=self.headers)

            if not response.status_code == 200:
                logger.warn(f'URL {url}: Response status {response.status_code}')
                break

            body = json.loads(response.text)

            if len(body) == 0:
                break

            self.add_to_cache(body, 'pulls')

            for pr_json in body:
                pr = GithubPull(pr_json)

                self.get_timeline(pr.number)

                prs.append(pr)

        prs = sorted(prs, key=lambda x: x.number, reverse=False)

        return prs

    def get_pr_comments(self, pr_num) -> typing.List[GithubComment]:
        url = COMMENTS_URL.format(self.repo, pr_num)
        response = requests.get(url, headers=self.headers)

        if not response.status_code == 200:
            logger.debug(f'Comments request failed with status "{response.status_code}"')
            return None

        body = json.loads(response.text)
        self.add_to_cache(body, 'pull_comments')

        return [GithubComment(x) for x in body]

    def get_pr_diff(self, pr_num) -> str:
        url = PULLS_URL.format(self.repo, pr_num)
        response = requests.get(url, headers=self.headers_diff)

        if not response.status_code == 200:
            return None

        return response.text

    def get_pr_files(self, pr_num: int) -> typing.List[GithubFile]:
        url = FILES_URL.format(self.repo, pr_num)
        response = requests.get(url, headers=self.headers)

        if not response.status_code == 200:
            logger.debug(f'PR files request failed with status "{response.status_code}"')
            return None

        body = json.loads(response.text)

        self.add_to_cache(body, 'pull_files')

        return [GithubFile(x) for x in body]
