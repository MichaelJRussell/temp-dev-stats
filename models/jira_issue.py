from datetime import datetime

class JiraIssue:
    key: str
    id: int
    issue_type_name: str
    project_name: str
    created: datetime
    summary: str
    priority: str

    def __init__(self, data) -> None:
        fields = data['fields']

        self.key = data['key']
        self.id = data['id']
        self.issue_type_name = fields['issuetype']['name']
        self.project_name = fields['project']['name']
        self.created = fields['created']
        self.summary = fields['summary']
        self.priority = fields['priority']['name']
