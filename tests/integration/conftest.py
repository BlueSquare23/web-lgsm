import time
import pytest

from app.infrastructure.persistence.models.game_server_model import GameServerModel


@pytest.fixture()
def cleanup_installed_servers(client, db_session):
    """
    Safety-net teardown for tests that install real game servers.

    Tests append a server_id to the returned list as soon as they know it
    (right after the install creates the DB row). On teardown -- whether
    the test passed, failed, or errored -- any server_id still present in
    the DB gets deleted through the real /api/delete route, so its
    on-disk install dir, tmux session, and OS user get torn down too, not
    just the DB row. Tests that already clean up after themselves on the
    happy path are unaffected: by the time teardown runs the server is
    already gone, so this is a no-op.

    Depends on db_session so its finalizer runs before db_session's own
    (pytest tears fixtures down in reverse dependency order) -- i.e.
    before the DB gets rolled back/dropped out from under us.
    """
    server_ids = []

    yield server_ids

    leftover = [
        sid for sid in server_ids
        if GameServerModel.query.filter_by(id=sid).first() is not None
    ]

    if not leftover:
        return

    for server_id in leftover:
        try:
            response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
            print(f"cleanup: deleted leftover server {server_id}, status={response.status_code}")
        except Exception as e:
            print(f"cleanup: failed to delete leftover server {server_id}: {e}")

    time.sleep(20)  # Give the delete job(s) time to actually finish.
