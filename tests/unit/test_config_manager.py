# test_config_manager.py
import pytest
import os
import tempfile
import configparser
from app.config.config_manager import ConfigManager
from app.config.defaults import DEFAULTS

class TestConfigManager:

    def create_test_config(self, content=None):
        """Helper to create temporary config files for testing"""
        if content is None:
            content = {
                'aesthetic': {
                    'text_color': '#0000ff',
                    'terminal_height': '15'
                },
                'settings': {
                    'remove_files': 'True',
                    'delete_user': 'False'
                }
            }

        # Create main.conf
        self.config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
        self.config_file.close()

        config = configparser.ConfigParser()
        for section, options in content.items():
            config.add_section(section)
            for key, value in options.items():
                config.set(section, key, value)

        with open(self.config_file.name, 'w') as f:
            config.write(f)

        return self.config_file.name

    def cleanup_test_config(self):
        """Clean up temporary config files"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file.name):
            os.unlink(self.config_file.name)

    def test_init_with_defaults(self):
        """Test initialization with default values"""
        # This will use the actual main.conf if it exists, or rely on defaults
        config = ConfigManager()
        assert config.config_file == "main.conf.local"
        assert config.config_local == "main.conf.local"

    def test_get_with_default_fallback(self):
        """Test get method with default fallback values"""
        config = ConfigManager()

        # Test getting a value that should use defaults
        text_color = config.get('aesthetic', 'text_color')
        assert text_color == DEFAULTS['aesthetic']['text_color']

        show_stats = config.getboolean('aesthetic', 'show_stats')
        assert show_stats == DEFAULTS['aesthetic']['show_stats']

    def test_get_with_custom_fallback(self):
        """Test get method with custom fallback values"""
        config = ConfigManager()

        # Test with custom fallback
        custom_value = config.get('settings', 'option', 'custom_fallback')
        assert custom_value == 'custom_fallback'

    def test_getboolean(self):
        """Test getboolean method"""
        config = ConfigManager()

        # Test boolean default
        show_stats = config.getboolean('aesthetic', 'show_stats')
        assert show_stats is True

        # Test with custom fallback
        custom_bool = config.getboolean('aesthetic', 'option', True)
        assert custom_bool is True

    def test_getint(self):
        """Test getint method"""
        config = ConfigManager()

        # Test integer default
        terminal_height = config.getint('aesthetic', 'terminal_height')
        assert terminal_height == 10

        # Test with custom fallback
        custom_int = config.getint('aesthetic', 'option', 42)
        assert custom_int == 42

    def test_set_method(self):
        """Test setting configuration values"""
        config_file = self.create_test_config()
        config = ConfigManager()
        # Override the config file path for testing
        config.config_file = config_file

        # Test setting a value
        config.set('aesthetic', 'text_color', '#ff0000')

        # Verify the value was set
        new_color = config.get('aesthetic', 'text_color')
        assert new_color == '#ff0000'

        self.cleanup_test_config()

    def test_section_access(self):
        """Test accessing entire sections"""
        config_file = self.create_test_config()
        config = ConfigManager()
        config.config_file = config_file

        section = config['aesthetic']
        assert 'text_color' in section
        assert 'terminal_height' in section

        self.cleanup_test_config()

    def test_nonexistent_section(self):
        """Test accessing non-existent section"""
        config = ConfigManager()

        with pytest.raises(KeyError):
            _ = config['nonexistent_section']

    def test_batch_update_context(self):
        """Test batch update context manager"""
        config_file = self.create_test_config()
        config = ConfigManager()
        config.config_file = config_file

        # Use batch update context
        with config.batch_update():
            config.set('aesthetic', 'text_color', '#ff0000', immediate=False)
            config.set('aesthetic', 'terminal_height', '20', immediate=False)
            # Values should not be written until context exit

        # Verify values were written after context exit
        assert config.get('aesthetic', 'text_color') == '#ff0000'
        assert config.getint('aesthetic', 'terminal_height') == 20

        self.cleanup_test_config()

    def test_reload_method(self):
        """Test that reload method works"""
        config_file = self.create_test_config()
        config = ConfigManager()
        config.config_file = config_file

        initial_value = config.get('aesthetic', 'text_color')

        # Modify the config file directly
        direct_config = configparser.ConfigParser()
        direct_config.read(config_file)
        direct_config.set('aesthetic', 'text_color', '#00ff00')
        with open(config_file, 'w') as f:
            direct_config.write(f)

        # Reload and check new value
        config.reload()
        new_value = config.get('aesthetic', 'text_color')
        assert new_value == '#00ff00'

        self.cleanup_test_config()

    def teardown_method(self):
        """Clean up after each test method"""
        self.cleanup_test_config()
