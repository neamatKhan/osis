##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

from decimal import Decimal
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from base.tests.factories.campus import CampusFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.proposal_folder import ProposalFolderFactory
from base.models.enums import organization_type, proposal_type, proposal_state, entity_type, \
    learning_container_year_types, learning_unit_year_quadrimesters, entity_container_year_link_type, \
    learning_unit_periodicity, internship_subtypes, learning_unit_year_subtypes
from base.forms.learning_unit_proposal import LearningUnitProposalModificationForm
from reference.tests.factories.language import LanguageFactory
from base.models import proposal_folder, proposal_learning_unit, entity_container_year


PROPOSAL_TYPE = proposal_type.ProposalType.TRANSFORMATION_AND_MODIFICATION.name
PROPOSAL_STATE = proposal_state.ProposalState.FACULTY.name


class TestSave(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        an_organization = OrganizationFactory(type=organization_type.MAIN)
        self.learning_unit_year = LearningUnitYearFakerFactory(credits=5, subtype=learning_unit_year_subtypes.FULL)
        self.learning_unit_year.learning_container_year.container_type = learning_container_year_types.COURSE
        self.learning_unit_year.learning_container_year.save()
        self.learning_unit_year.learning_container_year.campus.organization = an_organization
        self.learning_unit_year.learning_container_year.campus.is_administration = True
        self.learning_unit_year.learning_container_year.campus.save()

        self.entity_container_year = EntityContainerYearFactory(
            learning_container_year=self.learning_unit_year.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )

        today = datetime.date.today()
        an_entity = EntityFactory(organization=an_organization)
        self.entity_version = EntityVersionFactory(entity=an_entity, entity_type=entity_type.SCHOOL, start_date=today,
                                                   end_date=today.replace(year=today.year + 1))

        self.language = LanguageFactory(code="EN")
        self.campus = CampusFactory(name="OSIS Campus", organization=OrganizationFactory(type=organization_type.MAIN),
                                    is_administration=True)

        self.form_data = {
            "academic_year": self.learning_unit_year.academic_year.id,
            "first_letter": "L",
            "acronym": "OSIS1245",
            "title": "New title",
            "title_english": "New title english",
            "container_type": self.learning_unit_year.learning_container_year.container_type,
            "internship_subtype": "",
            "credits": "4",
            "periodicity": learning_unit_periodicity.BIENNIAL_ODD,
            "status": False,
            "language": self.language.id,
            "quadrimester": learning_unit_year_quadrimesters.Q1,
            "campus": self.campus.id,
            "requirement_entity": self.entity_version.id,
            "folder_entity": self.entity_version.id,
            "folder_id": "1",
        }

    def test_invalid_form(self):
        del self.form_data['academic_year']

        form = LearningUnitProposalModificationForm(self.form_data)
        with self.assertRaises(ValueError):
            form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

    def test_learning_unit_update(self):
        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        self.learning_unit_year.refresh_from_db()

        self.assertEqual(self.learning_unit_year.learning_unit.periodicity, self.form_data['periodicity'])

    def test_learning_unit_year_update(self):
        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        self.learning_unit_year.refresh_from_db()

        self.assertEqual(self.learning_unit_year.acronym,
                         "{}{}".format(self.form_data['first_letter'], self.form_data['acronym']))
        self.assertEqual(self.learning_unit_year.title, self.form_data['title'])
        self.assertEqual(self.learning_unit_year.title_english, self.form_data['title_english'])
        self.assertFalse(self.learning_unit_year.status)
        self.assertEqual(self.learning_unit_year.credits, Decimal(self.form_data['credits']))
        self.assertEqual(self.learning_unit_year.quadrimester, self.form_data['quadrimester'])

    def test_learning_container_update(self):
        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        self.learning_unit_year.refresh_from_db()
        learning_container_year = self.learning_unit_year.learning_container_year

        self.assertEqual(learning_container_year.acronym,
                         "{}{}".format(self.form_data['first_letter'], self.form_data['acronym']))
        self.assertEqual(learning_container_year.title, self.form_data['title'])
        self.assertEqual(learning_container_year.title_english, self.form_data['title_english'])
        self.assertEqual(learning_container_year.language, self.language)
        self.assertEqual(learning_container_year.campus, self.campus)

    def test_requirement_entity(self):
        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        self.entity_container_year.refresh_from_db()
        self.assertEqual(self.entity_container_year.entity, self.entity_version.entity)

    def test_with_all_entities_set(self):
        today = datetime.date.today()
        entity_1 = EntityFactory(organization=OrganizationFactory(type=organization_type.MAIN))
        additional_entity_version_1 = EntityVersionFactory(entity_type=entity_type.SCHOOL, start_date=today,
                                                           end_date=today.replace(year=today.year + 1),
                                                           entity=entity_1)
        entity_2 = EntityFactory(organization=OrganizationFactory(type=organization_type.MAIN))
        additional_entity_version_2 = EntityVersionFactory(entity_type=entity_type.SCHOOL, start_date=today,
                                                           end_date=today.replace(year=today.year + 1),
                                                           entity=entity_2)
        self.form_data["allocation_entity"] = self.entity_version.id
        self.form_data["additional_entity_1"] = additional_entity_version_1.id
        self.form_data["additional_entity_2"] = additional_entity_version_2.id

        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        entities_by_type = \
            entity_container_year.find_entities_grouped_by_linktype(self.learning_unit_year.learning_container_year)

        expected_entities = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: self.entity_version.entity,
            entity_container_year_link_type.ALLOCATION_ENTITY: self.entity_version.entity,
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: additional_entity_version_1.entity,
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: additional_entity_version_2.entity
        }
        self.assertDictEqual(entities_by_type, expected_entities)

    def test_modify_learning_container_subtype(self):
        self.form_data["container_type"] = learning_container_year_types.INTERNSHIP
        self.form_data["internship_subtype"] = internship_subtypes.TEACHING_INTERNSHIP

        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        self.learning_unit_year.refresh_from_db()

        self.assertEqual(self.learning_unit_year.learning_container_year.container_type,
                         learning_container_year_types.INTERNSHIP)
        self.assertEqual(self.learning_unit_year.internship_subtype, internship_subtypes.TEACHING_INTERNSHIP)

    def test_folder_creation(self):
        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        proposal_folder_created = proposal_folder.find_by_entity_and_folder_id(self.entity_version.entity, 1)

        self.assertTrue(proposal_folder_created)

    def test_folder_reuse(self):
        folder = ProposalFolderFactory(entity=self.entity_version.entity, folder_id=1)

        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        a_proposal_learning_unt = proposal_learning_unit.find_by_learning_unit_year(self.learning_unit_year)
        self.assertEqual(a_proposal_learning_unt.folder, folder)

    def test_creation_proposal_learning_unit(self):
        initial_data_expected = {
            "learning_container_year": {
                "id": self.learning_unit_year.learning_container_year.id,
                "acronym": self.learning_unit_year.acronym,
                "title": self.learning_unit_year.title,
                "title_english": self.learning_unit_year.title_english,
                "container_type": self.learning_unit_year.learning_container_year.container_type,
                "campus": self.learning_unit_year.learning_container_year.campus.id,
                "language": self.learning_unit_year.learning_container_year.language.id,
                "in_charge": self.learning_unit_year.learning_container_year.in_charge
            },
            "learning_unit_year": {
                "id": self.learning_unit_year.id,
                "acronym": self.learning_unit_year.acronym,
                "title": self.learning_unit_year.title,
                "title_english": self.learning_unit_year.title_english,
                "internship_subtype": self.learning_unit_year.internship_subtype,
                "credits": self.learning_unit_year.credits,
                "quadrimester": self.learning_unit_year.quadrimester,
            },
            "learning_unit": {
                "id": self.learning_unit_year.learning_unit.id,
                "periodicity": self.learning_unit_year.learning_unit.periodicity
            },
            "entities": {
                entity_container_year_link_type.REQUIREMENT_ENTITY: self.entity_container_year.entity.id,
                entity_container_year_link_type.ALLOCATION_ENTITY: None,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: None,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: None
            }
        }

        form = LearningUnitProposalModificationForm(self.form_data)
        form.save(self.learning_unit_year, self.person, PROPOSAL_TYPE, PROPOSAL_STATE)

        a_proposal_learning_unt = proposal_learning_unit.find_by_learning_unit_year(self.learning_unit_year)

        self.assertEqual(a_proposal_learning_unt.type, PROPOSAL_TYPE)
        self.assertEqual(a_proposal_learning_unt.state, PROPOSAL_STATE)
        self.assertEqual(a_proposal_learning_unt.author, self.person)

        self.assertDictEqual(a_proposal_learning_unt.initial_data, initial_data_expected)


class TestIsValid(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        an_organization = OrganizationFactory(type=organization_type.MAIN)
        self.learning_unit_year = LearningUnitYearFakerFactory(credits=5, subtype=learning_unit_year_subtypes.FULL)
        self.learning_unit_year.learning_container_year.container_type = learning_container_year_types.COURSE
        self.learning_unit_year.learning_container_year.save()
        self.learning_unit_year.learning_container_year.campus.organization = an_organization
        self.learning_unit_year.learning_container_year.campus.is_administration = True
        self.learning_unit_year.learning_container_year.campus.save()

        self.entity_container_year = EntityContainerYearFactory(
            learning_container_year=self.learning_unit_year.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )

        today = datetime.date.today()
        an_entity = EntityFactory(organization=an_organization)
        self.entity_version = EntityVersionFactory(entity=an_entity, entity_type=entity_type.SCHOOL, start_date=today,
                                                   end_date=today.replace(year=today.year + 1))

        self.language = LanguageFactory(code="EN")
        self.campus = CampusFactory(name="OSIS Campus", organization=OrganizationFactory(type=organization_type.MAIN),
                                    is_administration=True)

        self.form_data = {
            "academic_year": self.learning_unit_year.academic_year.id,
            "first_letter": "L",
            "acronym": "OSIS1245",
            "title": "New title",
            "title_english": "New title english",
            "container_type": self.learning_unit_year.learning_container_year.container_type,
            "internship_subtype": "",
            "credits": "4",
            "periodicity": learning_unit_periodicity.BIENNIAL_ODD,
            "status": False,
            "language": self.language.id,
            "quadrimester": learning_unit_year_quadrimesters.Q1,
            "campus": self.campus.id,
            "requirement_entity": self.entity_version.id,
            "folder_entity": self.entity_version.id,
            "folder_id": "1",
        }

    def test_internship_subtype(self):
        self.form_data["internship_subtype"] = internship_subtypes.TEACHING_INTERNSHIP
        form = LearningUnitProposalModificationForm(self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn(_("learning_unit_type_is_not_internship"), form.errors["internship_subtype"])









