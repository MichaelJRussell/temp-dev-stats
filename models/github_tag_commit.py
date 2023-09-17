class GithubTagCommit:
    sha: str
    author: str
    message: str

    def __init__(self, data: dict) -> None:
        self.sha = data['sha']
        self.author = data['commit']['author']['name']
        self.message = data['commit']['message']
