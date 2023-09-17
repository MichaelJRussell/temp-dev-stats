import typing

from models.github_user import GithubUser
from datetime import datetime

class GithubPull:
    user: GithubUser
    id: int
    number: int
    title: str
    state: str
    body: str
    created_at: datetime
    merged_at: datetime
    closed_at: datetime
    labels: typing.List[str]

    def __init__(self, pr_data) -> None:
        self.user = GithubUser(pr_data['user'])
        self.id = pr_data['id']
        self.number = pr_data['number']
        self.title = pr_data['title']
        self.state = pr_data['state']
        self.body = pr_data['body']
        self.created_at = datetime.strptime(pr_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        self.labels = []

        if not pr_data['merged_at'] == None:
            self.merged_at = datetime.strptime(pr_data['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
        else:
            self.merged_at = None
        if not pr_data['closed_at'] == None:
            self.closed_at = datetime.strptime(pr_data['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
        else:
            self.closed_at = None

        for gh_label in pr_data['labels']:
            self.labels.append(gh_label['name'])

    def __repr__(self) -> str:
        return f'{self.title} (#{self.number})'

    def __str__(self) -> str:
        return f'{self.title} (#{self.number})'
