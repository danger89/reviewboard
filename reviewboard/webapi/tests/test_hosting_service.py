from reviewboard.hostingsvcs.service import (get_hosting_services,
                                             get_hosting_service)
from reviewboard.webapi.resources import resources
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import (hosting_service_item_mimetype,
                                                hosting_service_list_mimetype)
from reviewboard.webapi.tests.mixins import BasicTestsMetaclass
from reviewboard.webapi.tests.urls import (get_hosting_service_item_url,
                                           get_hosting_service_list_url)


def _compare_item(self, item_rsp, hosting_service):
    self.assertEqual(item_rsp['id'], hosting_service.hosting_service_id)
    self.assertEqual(item_rsp['name'], hosting_service.name)
    self.assertEqual(item_rsp['needs_authorization'],
                     hosting_service.needs_authorization)
    self.assertEqual(item_rsp['supports_bug_trackers'],
                     hosting_service.supports_bug_trackers)
    self.assertEqual(item_rsp['supports_repositories'],
                     hosting_service.supports_repositories)
    self.assertEqual(item_rsp['supports_two_factor_auth'],
                     hosting_service.supports_two_factor_auth)
    self.assertEqual(item_rsp['supported_scmtools'],
                     hosting_service.supported_scmtools)

    plans_rsp = item_rsp['plans']
    plan_keys = set(plans_rsp.keys())

    if plan_keys == {''}:
        self.assertIsNone(hosting_service.plans)

        plan_rsp = plans_rsp['']
        self.assertEqual(plan_rsp['name'], 'Default')
        self.assertEqual(set(plan_rsp['fields']),
                         set(hosting_service.form.base_fields))
    else:
        plans = hosting_service.plans
        self.assertEqual(len(plans), len(plan_keys))

        for plan_id, plan in plans:
            self.assertIn(plan_id, plans_rsp)

            plan_rsp = plans_rsp[plan_id]
            self.assertEqual(plan_rsp['name'], plan['name'])
            self.assertEqual(set(plan_rsp['fields']),
                             set(plan['form'].base_fields))

    self.assertEqual(item_rsp['supported_scmtools'],
                     hosting_service.supported_scmtools)

    # Compute the base URL for links.
    url_base = 'http://testserver/'

    if '/s/local-site-1/' in item_rsp['links']['self']['href']:
        url_base += 's/local-site-1/'

    url_base += 'api/'

    # Check the links.
    accounts_url = url_base + ('hosting-service-accounts/?service=%s'
                               % hosting_service.hosting_service_id)
    self.assertIn('accounts', item_rsp['links'])
    self.assertEqual(item_rsp['links']['accounts']['href'], accounts_url)

    accounts_url = url_base + ('repositories/?hosting-service=%s'
                               % hosting_service.hosting_service_id)
    self.assertIn('repositories', item_rsp['links'])
    self.assertEqual(item_rsp['links']['repositories']['href'], accounts_url)


class ResourceListTests(BaseWebAPITestCase, metaclass=BasicTestsMetaclass):
    """Testing the HostingServiceResource list APIs."""
    fixtures = ['test_users']
    sample_api_url = 'hosting-services/'
    resource = resources.hosting_service

    compare_item = _compare_item

    def setup_http_not_allowed_list_test(self, user):
        return get_hosting_service_list_url()

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name,
                             populate_items):
        return (get_hosting_service_list_url(local_site_name),
                hosting_service_list_mimetype,
                get_hosting_services())


class ResourceItemTests(BaseWebAPITestCase, metaclass=BasicTestsMetaclass):
    """Testing the HostingServiceResource item APIs."""
    fixtures = ['test_users']
    sample_api_url = 'hosting-services/<id>/'
    resource = resources.hosting_service

    compare_item = _compare_item

    def setup_http_not_allowed_item_test(self, user):
        hosting_service = get_hosting_service('github')

        return get_hosting_service_item_url(hosting_service)

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name):
        hosting_service = get_hosting_service('github')

        return (get_hosting_service_item_url(hosting_service, local_site_name),
                hosting_service_item_mimetype,
                hosting_service)
