```
app
├── blueprints               # Route blueprints
│   ├── api
│   │   ├── __init__.py
│   │   ├── cmd_output.py
│   │   └── ...
│   ├── auth
│   │   ├── __init__.py
│   │   ├── edit_users.py
│   │   └── ...
│   └── main
│       ├── __init__.py
│       ├── about.py
│       └── ...
├── config
│   ├── __init__.py
│   ├── config_manager.py
│   └── ...
├── database.db
├── extensions.py
├── forms                    # Flask-WTForms classes
│   ├── auth.py
│   ├── helpers.py
│   └── views.py
├── __init__.py              # Flask app factory
├── models                   # Database models
│   ├── __init__.py
│   ├── audit.py
│   └── ...
├── paths.py
├── services
│   ├── __init__.py
│   ├── blocklist_service.py
│   └── ...
├── static
│   ├── css
│   │   └── main.css         # For custom non-bootstrap CSS.
│   ├── img
│   │   ├── action-half-life-header.jpg
│   │   ├── battlefield-1942-header.jpg
│   │   └── ...
│   └── js                   # Javascript dir for vanilla & Jquery scripts.
│       ├── alerts.js
│       ├── delete-btn.js
│       └── ... 
├── templates
│   ├── 2fa_setup.html
│   ├── about.html
│   └── ...
├── utils/                   # Helper classes/functions
│   ├── __init__.py
│   └── helpers.py
└── utils.py
```
