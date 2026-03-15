# Default config values. Put in here to keep class file clean.

DEFAULTS = {
    'aesthetic': {
        'text_color': '#09ff00',
        'terminal_height': '10',
        'graphs_primary': '#e01b24',
        'graphs_secondary': '#0d6efd',
        'show_stats': True,
        'show_barrel_roll': False
    },
    'settings': {
        'remove_files': False,
        'delete_user': True, 
        'show_stderr': True,
        'clear_output_on_reload': True,
        'cfg_editor': False,
        'send_cmd': False,
        'install_create_new_user': True,
        'end_in_newlines': True,
        'allow_custom_jobs': False
    },
    'debug': {
        'debug': False,
        'log_level': 'info'
    },
    'server': {
        'host': '127.0.0.1',
        'port': '12357'
    }
}
