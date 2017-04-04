description = "None"


class Backend(object):

    """
    This is the interface that all backends must implement. Depending on the
    actual backend, it's not mandatory to implement every method.
    """

    def __init__(self, data):
        self.data = data

    def submit(self, test_job):
        """
        Submits a given test job to the backend service.

        The return value  must be the job id as provided by the backend.
        """
        pass

    def fetch(self, test_job):
        """
        Fetches data from a given test job from the backend service. It can be
        assumed that the job has been properly submited before, i.e. it has a
        proper id.

        The return value must be a tuple (status, metadata, tests, metrics),
        where status is a string, all other elements are dictionaries.
        """
        pass

    def listen(self):
        """
        Listens the backend service for realtime test results. What to do with
        the received data is up to each specific backend implementation.
        """
        pass
