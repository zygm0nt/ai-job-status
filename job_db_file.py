import pickle
import os

DEFAULT_FILENAME = "JobDatabase.p"


class JobDatabaseFile:

    def __init__(self):
        if os.path.exists(DEFAULT_FILENAME):
            with open(DEFAULT_FILENAME, "rb") as f:
                self.job_database = pickle.load(f)
        else:
            self.job_database = set()

    def update(self, job_id):
        self.job_database.add(job_id)
        self._persist()

    def get_all(self):
        return self.job_database

    def _persist(self):
        with open(DEFAULT_FILENAME, "wb") as f:
            pickle.dump(self.job_database, f)