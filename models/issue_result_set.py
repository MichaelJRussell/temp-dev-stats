import typing

class IssueResultSet:
    startAt: int
    maxResults: int
    total: int
    issues: typing.List[typing.Dict[str, any]]

    def __init__(self, data: typing.Dict[str, any]):
        self.startAt = data['startAt']
        self.maxResults = data['maxResults']
        self.total = data['total']
        self.issues = data['issues']
