import typing
import requests
import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from models.issue_result_set import IssueResultSet
from pymongo import database

from models.jira_issue import JiraIssue

logger = logging.getLogger(__name__)

STORY_URL = 'https://globalvetlink.atlassian.net/rest/api/3/issue/{0}'
CREATE_URL = 'https://globalvetlink.atlassian.net/rest/api/3/issue'
SEARCH_URL = 'https://globalvetlink.atlassian.net/rest/api/3/search?{0}'
CHANGES_URL = 'https://globalvetlink.atlassian.net/rest/api/3/issue/{0}/changelog'

class JiraClient:
    cache_db: database.Database
    accept_headers: typing.Dict[str, str]
    content_headers: typing.Dict[str, str]
    basic_auth: HTTPBasicAuth

    def __init__(self, username: str, token: str, cache_db: database.Database) -> None:
        self.cache_db = cache_db

        self.accept_headers = { 'Accept': 'application/json' }
        self.content_headers = { 'Content-Type': 'application/json' }
        self.basic_auth = HTTPBasicAuth(username, token)

    def add_to_cache(self, data, collection: str = 'jira_issues'):
        if not self.cache_db:
            return

        if isinstance(data, list):
            for doc in data:
                query = {"id": doc["id"]}
                self.cache_db[collection].replace_one(query, doc, True)
        else:
            query = {"id": data["id"]}
            self.cache_db[collection].replace_one(query, data, True)

    def search(self, params: dict) -> IssueResultSet:
        query_pairs = []

        for k, v in params.items():
            query_pairs.append(f'{k}={v}')

        query_string = '&'.join(query_pairs)

        url = SEARCH_URL.format(query_string)
        response = requests.get(url, headers=self.accept_headers, auth=self.basic_auth)

        if not response.status_code == 200:
            logger.debug(f'Jira search request failed with status "{response.status_code}"')
            return None

        body = json.loads(response.text)
        result_set = IssueResultSet(body)

        self.add_to_cache(result_set.issues)

        return result_set

    def get_changelogs(self, key: str) -> typing.List[dict]:
        url = CHANGES_URL.format(key)
        response = requests.get(url, headers=self.accept_headers, auth=self.basic_auth)

        if not response.status_code == 200:
            logger.debug(f'Jira search request failed with status "{response.status_code}"')
            return None

        body = json.loads(response.text)

        return body['values']

    def get_issue(self, key: str) -> JiraIssue:
        url = STORY_URL.format(key)
        response = requests.get(url, headers=self.accept_headers, auth=self.basic_auth)

        if not response.status_code == 200:
            logger.warning(f'Jira story request failed with status "{response.status_code}"')
            return None

        body = json.loads(response.text)
        self.add_to_cache(body)

        return JiraIssue(body)
