import markdown

class ChangelogReader():

    def read(self):
        """
        Reads in the local CHANGELOG.md file and returns its contents.

        Args:
            None

        Returns:
            str: Contents of CHANGELOG.md file or err str.
        """
        try:
            with open("CHANGELOG.md", "r") as file:
                contents = file.read()

            return markdown.markdown(contents)

        except Exception as e:
            return f"Problem reading CHANGELOG.md: {e}"

