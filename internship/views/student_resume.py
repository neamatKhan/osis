##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from base import models as mdl

from django.utils.translation import ugettext_lazy as _


@login_required
def internships_student_resume(request):

    return render(request, "student_search.html", {'s_noma': None,
                                                   's_name': None})


@login_required
def internships_student_search(request):
    s_noma = request.GET['s_noma']
    s_name = request.GET['s_name']
    students_list = []
    criteria_present = False

    if len(s_noma) <= 0:
        s_noma  =None
    else:
        criteria_present=True

    s_name = s_name.strip()
    if len(s_name) <= 0:
        s_name  =None
    else:
        criteria_present=True

    message = None
    if criteria_present:
        if s_noma is None and s_name:
            students_list = mdl.student.find_by(person_name=s_name)
        if  s_noma and s_name is None:
            students_list = mdl.student.find_by(registration_id=s_noma)
        if s_noma and s_name:
            students_list = mdl.student.find_by(registration_id=s_noma, person_name=s_name)
    else:
         message = "%s" % _('You must choose at least one criteria!')

    return render(request, "student_search.html",
                           {'s_noma':       s_noma,
                            's_name':       s_name,
                            'students':     students_list,
                            'init':         "0",
                            'message':      message})


@login_required
def internships_student_read(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    if student:
        for student in student:
            student.address = ""
            address = mdl.person_address.find_by_person(student.person)
            if address:
                student.address = address

    return render(request, "student_resume.html", {'student': student})