from app.domain.entities.job import Job

from app.infrastructure.system.cron.cron_scheduler import CronScheduler
from app.infrastructure.persistence.models.cron_model import CronModel
from app.infrastructure.persistence.repositories.cron_repo import SqlAlchemyCronRepository
from app.infrastructure.persistence.models.game_server_model import GameServerModel


class TestSqlAlchemyCronRepoistory:
    def test_create_job(self, db_session, client, add_mock_server):
        """Test creating a job and then listing it"""
        test_server = GameServerModel.query.first()
        cron_repo = SqlAlchemyCronRepository()

        # Create a test job
        job_data = {
            "job_id": None,
            "server_id": test_server.id,
            "command": "echo 'hello world'",
            "comment": "Test job",
            "schedule": "* * * * *"
        }

        # Test creating the job
        job = Job(**job_data)
        job_id = cron_repo.add(job)
        assert job_id 

        # Verify the job exists in database
        db_job = CronModel.query.first()
        assert db_job is not None
        assert db_job.command == "echo 'hello world'"
        assert db_job.server_id == test_server.id


    def test_delete_job(self, db_session, client, add_mock_server):
        """Test deleting a job"""
        test_server = GameServerModel.query.first()
        cron_repo = SqlAlchemyCronRepository()

        # Create a test job first
        job_data = {
            "job_id": None,
            "server_id": test_server.id,
            "command": "echo 'delete me'",
            "comment": "Delete test",
            "schedule": "* * * * *"
        }
        job = Job(**job_data)
        job_id = cron_repo.add(job)
        assert job_id 

        # Verify the job exists in database
        db_job = CronModel.query.first()
        assert db_job is not None
        assert db_job.command == "echo 'delete me'"
        assert db_job.server_id == test_server.id

        # Verify job exists
        assert CronModel.query.filter_by(id=job_id).first() is not None

        # Test deleting the job
        delete_result = cron_repo.delete(job_id)
        assert delete_result is True
        
        # Verify job is gone
        assert CronModel.query.filter_by(id=job_id).first() is None


# TODO: Move the CronScheduler tests into their own test file.
    def test_parse_cron_jobs_empty_input(self):
        """Test parse_cron_jobs with empty input"""
        cron_scheduler = CronScheduler()
        result = cron_scheduler.parse_cron_jobs("", "test_server_123")
        assert result == []


    def test_parse_cron_jobs_with_valid_job(self):
        """Test parse_cron_jobs with a valid cron job"""
        cron_scheduler = CronScheduler()
        cron_text = """#Ansible: test_server_123, job123, Test Job
        * * * * * echo "Hello World"
        """
        result = cron_scheduler.parse_cron_jobs(cron_text, "test_server_123")
        assert len(result) == 1
        assert result[0].server_id == "test_server_123"
        assert result[0].job_id == "job123"
        assert result[0].comment == "Test Job"
        assert result[0].command == 'echo "Hello World"'

# Broken will fix l8tr
#    def test_parse_cron_jobs_wrong_server(self):
#        """Test parse_cron_jobs with a job for a different server"""
#        cron_scheduler = CronScheduler()
#        cron_text = """#Ansible: wrong_uuid, job123, Test Job
#        * * * * * echo "Hello World"
#        """
#        result = cron_scheduler.parse_cron_jobs(cron_text, "6e5c5729-9f6a-49f0-863f-a6a30254bad5")
#        assert result == []


    def test_edit_existing_job(self, db_session, add_mock_server):
        """Test editing an existing job"""
        # Get the test server from the fixture
        test_server = GameServerModel.query.first()
        cron_repo = SqlAlchemyCronRepository()

        # Create initial job
        job_data = {
            "job_id": None,
            "server_id": test_server.id,
            "command": "echo 'original'",
            "comment": "Original job",
            "schedule": "0 * * * *"
        }
        job = Job(**job_data)
        job_id = cron_repo.add(job)

        # Edit the job
        updated_job = {
            "job_id": job_id,
            "server_id": test_server.id,
            "command": "echo 'updated'",
            "comment": "Updated job",
            "schedule": "5 * * * *"
        }
        job = Job(**updated_job)
        edit_result = cron_repo.update(job)
        assert edit_result is True

        # Verify changes
        db_job = CronModel.query.filter_by(id=job_id).first()
        assert db_job.command == "echo 'updated'"
        assert db_job.comment == "Updated job"
        assert db_job.schedule == "5 * * * *"
