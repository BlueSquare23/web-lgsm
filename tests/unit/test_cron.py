from app.cron import CronService
from app.models import GameServer, Job

class TestCronService:
    def test_create_job(self, db_session, client, add_mock_server):
        """Test creating a job and then listing it"""
        test_server = GameServer.query.first()
        cron_service = CronService(server_id=test_server.id)

        # Create a test job
        job_data = {
            "job_id": None,
            "server_id": test_server.id,
            "command": "echo 'hello world'",
            "comment": "Test job",
            "expression": "* * * * *"
        }

        # Test creating the job
        create_result = cron_service.edit_job(job_data)
        assert create_result is True

        # Verify the job exists in database

        db_job = Job.query.first()
        assert db_job is not None
        assert db_job.command == "echo 'hello world'"
        assert db_job.server_id == test_server.id


    def test_delete_job(self, db_session, client, add_mock_server):
        """Test deleting a job"""
        test_server = GameServer.query.first()
        cron_service = CronService(server_id=test_server.id)

        # Create a test job first
        job_data = {
            "job_id": None,
            "server_id": test_server.id,
            "command": "echo 'delete me'",
            "comment": "Delete test",
            "expression": "* * * * *"
        }
        cron_service.edit_job(job_data)
        jobs_list = cron_service.list_jobs()
        job_id = jobs_list[0]["job_id"]

        # Verify job exists
        assert Job.query.filter_by(id=job_id).first() is not None

        # Test deleting the job
        delete_result = cron_service.delete_job(job_id)
        assert delete_result is True
        
        # Verify job is gone
        assert Job.query.filter_by(id=job_id).first() is None


    def test_parse_cron_jobs_empty_input(self):
        """Test parse_cron_jobs with empty input"""
        cron_service = CronService(server_id="test_server_123")
        result = cron_service.parse_cron_jobs("", "test_server_123")
        assert result == []


    def test_parse_cron_jobs_with_valid_job(self):
        """Test parse_cron_jobs with a valid cron job"""
        cron_service = CronService(server_id="test_server_123")
        cron_text = """#Ansible: test_server_123, job123, Test Job
        * * * * * echo "Hello World"
        """
        result = cron_service.parse_cron_jobs(cron_text, "test_server_123")
        assert len(result) == 1
        assert result[0]['server_id'] == "test_server_123"
        assert result[0]['job_id'] == "job123"
        assert result[0]['comment'] == "Test Job"
        assert result[0]['command'] == 'echo "Hello World"'


    def test_parse_cron_jobs_wrong_server(self):
        """Test parse_cron_jobs with a job for a different server"""
        cron_service = CronService(server_id="test_server_123")
        cron_text = """#Ansible: other_server, job123, Test Job
        * * * * * echo "Hello World"
        """
        result = cron_service.parse_cron_jobs(cron_text, "test_server_123")
        assert result == []


    def test_edit_existing_job(self, db_session, add_mock_server):
        """Test editing an existing job"""
        # Get the test server from the fixture
        test_server = GameServer.query.first()
        cron_service = CronService(server_id=test_server.id)

        # Create initial job
        job_data = {
            "job_id": None,
            "server_id": test_server.id,
            "command": "echo 'original'",
            "comment": "Original job",
            "expression": "0 * * * *"
        }
        cron_service.edit_job(job_data)
        jobs_list = cron_service.list_jobs()
        job_id = jobs_list[0]["job_id"]

        # Edit the job
        updated_job = {
            "job_id": job_id,
            "server_id": test_server.id,
            "command": "echo 'updated'",
            "comment": "Updated job",
            "expression": "5 * * * *"
        }
        edit_result = cron_service.edit_job(updated_job)
        assert edit_result is True

        # Verify changes
        db_job = Job.query.filter_by(id=job_id).first()
        assert db_job.command == "echo 'updated'"
        assert db_job.comment == "Updated job"
        assert db_job.expression == "5 * * * *"
