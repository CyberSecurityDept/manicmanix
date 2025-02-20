class Artifact:
    """
    Main artifact class
    """

    def __init__(self, *args, **kwargs):
        self.results = []
        self.detected = []
        self.indicators = None
        super().__init__(*args, **kwargs)

    def parse(self, entry: str):
        """
        Parse the artifact, adds the parsed information to self.results
        """
        raise NotImplementedError

    def check_indicators(self) -> None:
        """Check the results of this module against a provided list of
        indicators coming from self.indicators
        """
        raise NotImplementedError
