class GithubFile:
    def __init__(self, file_data) -> None:
        self.filename = file_data['filename']
        self.status = file_data['status']
        self.additions = file_data['additions']
        self.deletions = file_data['deletions']
        self.changes = file_data['changes']
