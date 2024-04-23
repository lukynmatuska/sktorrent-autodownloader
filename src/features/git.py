"""Module for working with git"""
import git


class Git():
    """Class for working with git"""
    def __init__(self):
        self.repo = git.Repo(search_parent_directories=True)
        self.cmd = self.repo.git

    async def pull(self):
        """Pull"""
        return self.cmd.pull()

    def short_hash(self):
        """Get short hash of actual last commit"""
        return self.repo.head.object.hexsha[:7]
