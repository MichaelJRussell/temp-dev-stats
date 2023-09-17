class GithubUser:
    def __init__(self, pr_user) -> None:
        self.login = pr_user['login']
