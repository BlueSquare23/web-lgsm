class ListControls:

    def __init__(self, controls_repository):
        self.controls_repository = controls_repository

#TODO: Convert both of these to IDs and then fetch via ID in controls_repo.
    def execute(self, server, user):
        return self.controls_repository.list(server, user)

