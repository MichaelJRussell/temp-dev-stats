from models.github_user import GithubUser

class GithubComment:
    def __init__(self, comment_data) -> None:
        self.user = GithubUser(comment_data['user'])
        self.created_at = comment_data['created_at']
        self.body = comment_data['body']
