from collections import OrderedDict


from squad.core.utils import parse_name
from squad.core.models import Test


class TestResult(object):

    def __init__(self, test):
        self.status = test.status
        self.test_run = test.test_run


class TestHistory(object):

    def __init__(self, project, full_test_name):
        suite, test_name = parse_name(full_test_name)
        self.test = full_test_name

        tests = Test.objects.filter(
            suite__slug=suite,
            name=test_name,
            test_run__build__project=project,
        ).order_by(
            '-test_run__build__created_at',
            'test_run__environment_id'
        )
        Test.prefetch_related(tests)

        environments = OrderedDict()
        results = OrderedDict()
        for test in tests:
            build = test.test_run.build
            environment = test.test_run.environment

            environments[environment] = True

            if build not in results:
                results[build] = {}
            results[build][environment] = TestResult(test)

        self.environments = list(environments.keys())
        self.results = results
