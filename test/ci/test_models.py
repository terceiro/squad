from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from mock import patch, MagicMock


from squad.core import models as core_models


from squad.ci import models
from squad.ci.backend.null import Backend


class BackendTest(TestCase):

    def test_basics(self):
        models.Backend(
            url='http://example.com',
            username='foobar',
            token='mypassword'
        )

    def test_implementation(self):
        backend = models.Backend()
        impl = backend.get_implementation()
        self.assertIsInstance(impl, Backend)


NOW = timezone.now()


class BackendTestBase(TestCase):

    def setUp(self):
        self.group = core_models.Group.objects.create(slug='mygroup')
        self.project = self.group.projects.create(slug='myproject')
        self.backend = models.Backend.objects.create()

    def create_test_job(self, **attrs):
        return self.backend.test_jobs.create(target=self.project, **attrs)


class BackendPollTest(BackendTestBase):

    @patch('squad.ci.models.Backend.fetch')
    def test_poll(self, fetch_method):
        test_job = self.create_test_job(submitted=True)
        self.backend.poll()

        fetch_method.assert_called_with(test_job)

    @patch('squad.ci.models.Backend.fetch')
    def test_poll_wont_fetch_non_submitted_job(self, fetch_method):
        self.create_test_job(submitted=False)
        self.backend.poll()

        fetch_method.assert_not_called()

    @patch('squad.ci.models.Backend.fetch')
    def test_poll_wont_fetch_job_previouly_fetched(self, fetch_method):
        self.create_test_job(submitted=True, fetched=True)
        self.backend.poll()

        fetch_method.assert_not_called()


class BackendFetchTest(BackendTestBase):

    @patch('squad.ci.models.Backend.really_fetch')
    def test_poll_wont_fetch_before_poll_interval(self, fetch_method):
        test_job = self.create_test_job(submitted=True, last_fetch_attempt=NOW)
        self.backend.fetch(test_job)

        fetch_method.assert_not_called()

    @patch('squad.ci.models.Backend.really_fetch')
    def test_poll_will_fetch_after_poll_interval(self, fetch_method):
        past = timezone.now() - relativedelta(minutes=self.backend.poll_interval + 1)
        test_job = self.create_test_job(submitted=True, last_fetch_attempt=past)
        self.backend.fetch(test_job)

        fetch_method.assert_called_with(test_job)

    @patch('django.utils.timezone.now', return_value=NOW)
    @patch('squad.ci.models.Backend.get_implementation')
    def test_really_fetch(self, get_implementation, __now__):
        impl = MagicMock()
        impl.fetch = MagicMock()
        get_implementation.return_value = impl

        test_job = self.create_test_job()
        self.backend.really_fetch(test_job)

        test_job.refresh_from_db()
        self.assertEqual(NOW, test_job.last_fetch_attempt)
        self.assertTrue(test_job.fetched)

        get_implementation.assert_called()
        impl.fetch.assert_called()


class BackendSubmitTest(BackendTestBase):

    @patch('squad.ci.models.Backend.get_implementation')
    def test_submit(self, get_implementation):
        test_job = self.create_test_job()
        impl = MagicMock()
        impl.submit = MagicMock(return_value='999')
        get_implementation.return_value = impl

        self.backend.submit(test_job)
        test_job.refresh_from_db()

        impl.submit.assert_called()
        self.assertTrue(test_job.submitted)
        self.assertEqual('999', test_job.job_id)


class TestJobTest(TestCase):

    def test_basics(self):
        group = core_models.Group.objects.create(slug='mygroup')
        project = group.projects.create(slug='myproject')
        backend = models.Backend.objects.create(
            url='http://example.com',
            username='foobar',
            token='mypassword',
        )
        testjob = models.TestJob.objects.create(
            target=project,
            build='1',
            environment='myenv',
            backend=backend,
        )
        self.assertIsNone(testjob.job_id)
