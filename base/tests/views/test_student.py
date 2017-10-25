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
from unittest import mock
from unittest.mock import Mock

from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from requests.exceptions import RequestException

from base.tests.factories.student import StudentFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory


class StudentViewTestCase(TestCase):

    def setUp(self):
        self.program_manager_1 = ProgramManagerFactory()
        # Add permission
        user = self.program_manager_1.person.user
        permission = Permission.objects.get(name='Can access student')
        user.user_permissions.add(permission)
        self.students_db = [StudentFactory() for i in range(10)]

    @mock.patch('base.views.layout.render')
    def test_students(self,  mock_render):
        request_factory = RequestFactory()

        request = request_factory.get(reverse('students'))
        request.user = self.program_manager_1.person.user

        from base.views.student import students

        students(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'student/students.html')

    @mock.patch('base.views.layout.render')
    def test_students(self, mock_render):

        request_factory = RequestFactory()
        request = request_factory.get(reverse('students'))
        request.user = self.program_manager_1.person.user

        from base.views.student import students

        students(request)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'student/students.html')
        self.assertIsNone(context['students'])

    @mock.patch('base.views.layout.render')
    def test_students_search(self, mock_render):
        from base.views.student import student_search

        request_factory = RequestFactory()
        request = request_factory.get(reverse(student_search), data={
            'registration_id': self.students_db[0].registration_id}
                                      )
        request.user = self.program_manager_1.person.user

        student_search(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'student/students.html')
        self.assertEqual(context['students'], [self.students_db[0]])

        request_factory = RequestFactory()
        request = request_factory.get(reverse(student_search), data={
            'name': self.students_db[1].person.last_name[:2]}
                                      )
        request.user = self.program_manager_1.person.user

        student_search(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'student/students.html')
        self.assertIn(self.students_db[1], context['students'])

        request_factory = RequestFactory()
        request = request_factory.get(reverse(student_search))
        request.user = self.program_manager_1.person.user

        student_search(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'student/students.html')
        self.assertIsNone(context['students'])

    @mock.patch('base.views.layout.render')
    def test_student_read(self,  mock_render):
        student = StudentFactory(person=PersonFactory(last_name='Durant', first_name='Thomas'))

        request_factory = RequestFactory()
        request = request_factory.get(reverse('student_read', args=[student.id]))
        request.user = self.program_manager_1.person.user

        from base.views.student import student_read

        student_read(request, student.id)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'student/student.html')
        self.assertEqual(context['student'], student)

    @mock.patch('requests.get', side_effect=RequestException)
    def test_student_picture_unknown(self, mock_request_get):
        student_m = StudentFactory(person=PersonFactory(last_name='Durant', first_name='Thomas', gender='M'))
        student_f = StudentFactory(person=PersonFactory(last_name='Durant', first_name='Alice', gender='F'))

        from base.views.student import student_picture
        from django.contrib.staticfiles.storage import staticfiles_storage

        request = RequestFactory().get(reverse(student_picture, args=[student_m.id]))
        request.user = self.program_manager_1.person.user
        response = student_picture(request, student_m.id)

        self.assertTrue(mock_request_get.called)
        self.assertEqual(response.url, staticfiles_storage.url('img/men_unknown.png'))

        request = RequestFactory().get(reverse(student_picture, args=[student_f.id]))
        request.user = self.program_manager_1.person.user
        response = student_picture(request, student_f.id)

        self.assertTrue(mock_request_get.called)
        self.assertEqual(response.url, staticfiles_storage.url('img/women_unknown.png'))

    @mock.patch('requests.get')
    def test_student_picture(self, mock_request_get):
        student_m = StudentFactory(person=PersonFactory(last_name='Durant', first_name='Thomas', gender='M'))

        from base.views.student import student_picture

        mock_response = Mock()
        mock_response.json.return_value = {'photo_url': 'awesome/photo.png'}
        mock_response.content = b"an image"
        mock_response.status_code = 200
        mock_request_get.return_value = mock_response

        request = RequestFactory().get(reverse(student_picture, args=[student_m.id]))
        request.user = self.program_manager_1.person.user
        response = student_picture(request, student_m.id)

        self.assertTrue(mock_request_get.called)
        self.assertEqual(response.content, b'an image')

    def test_student_picture_for_non_existent_student(self):
        non_existent_student_id = 666
        request = RequestFactory().get(reverse('student_picture', args=[non_existent_student_id]))
        request.user = self.program_manager_1.person.user

        from base.views.student import student_picture
        from django.http import Http404

        self.assertRaises(Http404, student_picture, request, non_existent_student_id)
