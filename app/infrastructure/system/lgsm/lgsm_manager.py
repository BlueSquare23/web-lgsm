import os
import time
import requests

class LgsmManager:
    LINUXGSM_URL = "https://linuxgsm.sh"
    THREE_WEEKS_SECONDS = 1814400

    def __init__(self, logger):
        self.logger = logger

    def get_lgsmsh(self, lgsmsh_path):
        """
        Fetch the latest linuxgsm.sh script and make it executable.
        """
        try:
            headers = {"User-Agent": "Wget/1.20.3 (linux-gnu)"}
            response = requests.get(self.LINUXGSM_URL, headers=headers)
            response.raise_for_status()

            with open(lgsmsh_path, "wb") as f:
                f.write(response.content)

            os.chmod(lgsmsh_path, 0o755)

            self.logger.info("Latest linuxgsm.sh script fetched!")

        except Exception as e:
            self.logger.debug(e)

    def check_and_get_lgsmsh(self, lgsmsh_path):
        """
        Ensure linuxgsm.sh exists and is fresh (<= 3 weeks old).
        """
        if not os.path.isfile(lgsmsh_path):
            self.get_lgsmsh(lgsmsh_path)
            return

        age = time.time() - os.path.getmtime(lgsmsh_path)

        if age > self.THREE_WEEKS_SECONDS:
            self.get_lgsmsh(lgsmsh_path)
