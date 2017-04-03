import io
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase
from openpyxl.writer.excel import save_virtual_workbook

from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.organization_address import OrganizationAddressFactory


# This test case is just for the validation of the urls, the parameters and the templates.
from internship.tests.factories.speciality import SpecialityFactory
from internship.tests.utils.test_upload_xls import XlsPlaceImportTestCase


class PlaceViewAndUrlTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        self.cohort = CohortFactory()

    def test_home(self):
        kwargs = {'cohort_id': self.cohort.id, }
        url = reverse('internships_places', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'places.html')

    def test_student_affectation(self):
        organization = OrganizationFactory(cohort=self.cohort)
        kwargs = {
            'cohort_id': self.cohort.id,
            'organization_id': organization.id
        }
        url = reverse('place_detail_student_affectation', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_detail_affectation.html')

    def test_student_choice(self):
        organization = OrganizationFactory(cohort=self.cohort)
        kwargs = {
            'cohort_id': self.cohort.id,
            'organization_id': organization.id
        }
        url = reverse('place_detail_student_choice', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_detail.html')

    def test_create(self):
        kwargs = {
            'cohort_id': self.cohort.id
        }
        url = reverse('place_create', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_form.html')

    def test_edit(self):
        organization = OrganizationFactory(cohort=self.cohort)
        organization_address = OrganizationAddressFactory(organization=organization)

        kwargs = {
            'cohort_id': self.cohort.id,
            'organization_id': organization.id
        }
        url = reverse('place_edit', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_form.html')

    def test_save(self):
        organization = OrganizationFactory(cohort=self.cohort)
        organization_address = OrganizationAddressFactory(organization=organization)

        kwargs = {
            'cohort_id': self.cohort.id,
            'organization_id': organization.id,
            'organization_address_id': organization_address.id,
        }
        url = reverse('place_save', kwargs=kwargs)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_form.html')

    def test_new(self):
        url = reverse('place_save_new', kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_places_stud(self):
        url = reverse('internships_places_stud', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_places_file(self):
        url = reverse('upload_places', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_places_file(self):
        workbook = XlsPlaceImportTestCase.generate_workbook()

        content_of_workbook = io.BytesIO(save_virtual_workbook(workbook))
        content_of_workbook.name = 'demo.xls'

        url = reverse('upload_places', kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.post(url, {'file': content_of_workbook}, follow=True)

        # print(response.status_code)
        self.assertRedirects(response, reverse('internships_places', kwargs={
            'cohort_id': self.cohort.id,
        }))

    def test_export_xls_affectation(self):
        organization = OrganizationFactory(cohort=self.cohort)
        speciality = SpecialityFactory()

        url = reverse('affectation_download', kwargs={
            'cohort_id': self.cohort.id,
            'organization_id': organization.id,
            'speciality_id': speciality.id,
        })

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_export_xls_organisation_affectation(self):
        organization = OrganizationFactory(cohort=self.cohort)

        url = reverse('organisation_affectation_download', kwargs={
            'cohort_id': self.cohort.id,
            'organization_id': organization.id,
        })

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
