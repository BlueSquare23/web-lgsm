from app import create_app
from app.services.sudoers_service import SudoersService

app = create_app()

with app.app_context():
    username = 'mcserver'
    sudoers_service = SudoersService(username)
    
    print(sudoers_service.has_access())
