class Stats:
    def __init__(
            self, total_words=None, total_unknown=None, comprehension=None, total_unique=None, unique_unknown=None
    ):
        self.total_words = total_words or "-"
        self.total_unknown = total_unknown or "-"
        self.comprehension = comprehension or "-"
        self.total_unique = total_unique or "-"
        self.unique_unknown = unique_unknown or "-"
