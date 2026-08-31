class ReadChangelog:

    def __init__(self, changelog_reader):
        self.changelog_reader = changelog_reader

    def execute(self):
        return self.changelog_reader.read()

