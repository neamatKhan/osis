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
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from base import models as mdl
from dissertation.models import adviser, dissertation, faculty_adviser, offer_proposition, proposition_dissertation,\
    proposition_document_file, proposition_role
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_role import PropositionRole
from dissertation.forms import PropositionDissertationForm, ManagerPropositionDissertationForm,\
    ManagerPropositionRoleForm, ManagerPropositionDissertationEditForm
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
from django.contrib.auth.decorators import user_passes_test
from base.views import layout
import time
from django.http import HttpResponse


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    this_adviser = adviser.search_by_person(person)
    return this_adviser.type == 'MGR' if this_adviser else False


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_teacher(user):
    person = mdl.person.find_by_user(user)
    this_adviser = adviser.search_by_person(person)
    return this_adviser.type == 'PRF' if this_adviser else False

###########################
#      MANAGER VIEWS      #
###########################


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    propositions = proposition_dissertation.search_by_offer(offers)
    return layout.render(request, 'manager_proposition_dissertations_list.html',
                         {'proposition_dissertations': propositions})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_delete(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    proposition.deactivate()
    return redirect('manager_proposition_dissertations')


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_detail(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_use = dissertation.count_by_proposition(proposition)
    percent = count_use * 100 / proposition.max_number_student
    count_proposition_role = proposition_role.count_by_proposition(proposition)
    files = proposition_document_file.find_by_proposition(proposition)
    filename = ""
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role < 1:
        proposition_role.add('PROMOTEUR', proposition.author, proposition)
    proposition_roles = proposition_role.search_by_proposition(proposition)
    return layout.render(request, 'manager_proposition_dissertation_detail.html',
                         {'proposition_dissertation': proposition,
                          'adviser': adv,
                          'count_use': count_use,
                          'percent': round(percent, 2),
                          'proposition_roles': proposition_roles,
                          'count_proposition_role': count_proposition_role,
                          'filename': filename})


@login_required
@user_passes_test(is_manager)
def manage_proposition_dissertation_edit(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    if request.method == "POST":
        form = ManagerPropositionDissertationEditForm(request.POST, instance=proposition)
        if form.is_valid():
            proposition = form.save()
            return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)
    else:
        form = ManagerPropositionDissertationEditForm(instance=proposition)
    return layout.render(request, 'manager_proposition_dissertation_edit.html',
                         {'prop_dissert': proposition,
                          'form': form,
                          'author': proposition.author,
                          'types_choices': PropositionDissertation.TYPES_CHOICES,
                          'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                          'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_jury_edit(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)
    proposition = prop_role.proposition_dissertation
    return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_jury_new(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    count_proposition_role = PropositionRole.objects.filter(proposition_dissertation=proposition).count()
    if request.method == "POST":
        form = ManagerPropositionRoleForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            status = data['status']
            adv = data['adviser']
            prop = data['proposition_dissertation']
            if status == "PROMOTEUR":
                proposition.set_author(adv)
                proposition_role.delete(status, prop)
                proposition_role.add(status, adv, prop)
            elif count_proposition_role < 4:
                proposition_role.add(status, adv, prop)
            return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)
        else:
            form = ManagerPropositionRoleForm(initial={'proposition_dissertation': proposition})
    else:
        form = ManagerPropositionRoleForm(initial={'proposition_dissertation': proposition})
    return layout.render(request, 'manager_proposition_dissertations_jury_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_role_delete(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)
    proposition = prop_role.proposition_dissertation
    prop_role.delete()
    return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_new(request):
    if request.method == "POST":
        person = mdl.person.find_by_user(request.user)
        form = ManagerPropositionDissertationForm(request.POST)
        if form.is_valid():
            proposition = form.save()
            proposition.set_creator(person)
            return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)
        else:
            form = ManagerPropositionDissertationForm(initial={'active': True})
            adv = adviser.search_by_person(person)
            offers = faculty_adviser.search_by_adviser(adv)
            form.fields["offer_proposition"].queryset = offer_proposition.search_by_offer(offers)
            return layout.render(request, 'manager_proposition_dissertation_new.html',
                                 {'form': form,
                                  'types_choices': PropositionDissertation.TYPES_CHOICES,
                                  'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                                  'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})
    else:
        form = ManagerPropositionDissertationForm(initial={'active': True})
        person = mdl.person.find_by_user(request.user)
        adv = adviser.search_by_person(person)
        offers = faculty_adviser.search_by_adviser(adv)
        form.fields["offer_proposition"].queryset = offer_proposition.search_by_offer(offers)
        return layout.render(request, 'manager_proposition_dissertation_new.html',
                             {'form': form,
                              'types_choices': PropositionDissertation.TYPES_CHOICES,
                              'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                              'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_search(request):
    propositions = proposition_dissertation.search(terms=request.GET['search'], active=True)
    if 'bt_xlsx' in request.GET:
        filename = "%s%s%s" % ('EXPORT_dissertation_', time.strftime("%Y-%m-%d %H:%M"), '.xlsx')
        workbook = Workbook(encoding='utf-8')
        worksheet1 = workbook.active
        worksheet1.title = "proposition_dissertation"
        worksheet1.append(['Date_de_création', 'Teacher', 'Title',
                           'Type', 'Level', 'Collaboration', 'Max_number_student', 'Visibility',
                           'Active', 'Programme(s)', 'Description'])
        for proposition in propositions:
            worksheet1.append([proposition.created_date,
                               str(proposition.author),
                               proposition.title,
                               proposition.type,
                               proposition.level,
                               proposition.collaboration,
                               proposition.max_number_student,
                               proposition.visibility,
                               proposition.active,
                               ', '.join((str(conv.acronym) for conv in proposition.offer_proposition.all()))])
        response = HttpResponse(save_virtual_workbook(workbook), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
        return response

    else:
        return layout.render(request, "manager_proposition_dissertations_list.html",
                             {'proposition_dissertations': propositions})

###########################
#      TEACHER VIEWS      #
###########################


@login_required
@user_passes_test(is_teacher)
def proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    propositions = proposition_dissertation.get_all_for_teacher(adv)
    return layout.render(request, 'proposition_dissertations_list.html',
                         {'proposition_dissertations': propositions})


@login_required
@user_passes_test(is_teacher)
def proposition_dissertation_delete(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    proposition.deactivate()
    return redirect('proposition_dissertations')


@login_required
@user_passes_test(is_teacher)
def proposition_dissertation_detail(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_use = dissertation.count_by_proposition(proposition)
    percent = count_use * 100 / proposition.max_number_student
    count_proposition_role = proposition_role.count_by_proposition(proposition)
    files = proposition_document_file.find_by_proposition(proposition)
    filename = ""
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role < 1:
        proposition_role.add('PROMOTEUR', proposition.author, proposition)
    proposition_roles = proposition_role.search_by_proposition(proposition)
    return layout.render(request, 'proposition_dissertation_detail.html',
                         {'proposition_dissertation': proposition,
                          'adviser': adv,
                          'count_use': count_use,
                          'percent': round(percent, 2),
                          'proposition_roles': proposition_roles,
                          'count_proposition_role': count_proposition_role,
                          'filename': filename})


@login_required
@user_passes_test(is_teacher)
def proposition_dissertation_edit(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    if proposition.author == adv or proposition.creator == adv.person:
        if request.method == "POST":
            form = PropositionDissertationForm(request.POST, instance=proposition)
            if form.is_valid():
                proposition = form.save()
                return redirect('proposition_dissertation_detail', pk=proposition.pk)
        else:
            form = PropositionDissertationForm(instance=proposition)
        return layout.render(request, 'proposition_dissertation_edit.html',
                             {'prop_dissert': proposition,
                              'form': form,
                              'types_choices': PropositionDissertation.TYPES_CHOICES,
                              'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                              'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})
    else:
        return redirect('proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(is_teacher)
def my_dissertation_propositions(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    propositions = proposition_dissertation.get_mine_for_teacher(adv)
    return layout.render(request, 'proposition_dissertations_list_my.html',
                         {'proposition_dissertations': propositions})


@login_required
@user_passes_test(is_teacher)
def proposition_dissertations_created(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    propositions = proposition_dissertation.get_created_for_teacher(adv)
    return layout.render(request, 'proposition_dissertations_list_created.html',
                         {'proposition_dissertations': propositions})


@login_required
@user_passes_test(is_teacher)
def proposition_dissertation_new(request):
    person = mdl.person.find_by_user(request.user)
    if request.method == "POST":
        form = PropositionDissertationForm(request.POST)
        if form.is_valid():
            proposition = form.save()
            proposition.set_creator(person)
            return redirect('proposition_dissertation_detail', pk=proposition.pk)
    else:
        adv = adviser.search_by_person(person)
        form = PropositionDissertationForm(initial={'author': adv, 'active': True})
    return layout.render(request, 'proposition_dissertation_new.html',
                         {'form': form,
                          'types_choices': PropositionDissertation.TYPES_CHOICES,
                          'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                          'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})


@login_required
@user_passes_test(is_teacher)
def proposition_dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    propositions = proposition_dissertation.search(terms=request.GET['search'],
                                                   active=True, visibility=True, connected_adviser=adv)
    return layout.render(request, "proposition_dissertations_list.html",
                         {'proposition_dissertations': propositions})


@login_required
@user_passes_test(is_teacher)
def proposition_dissertations_jury_edit(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)
    proposition = prop_role.proposition_dissertation
    return redirect('proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(is_teacher)
def proposition_dissertations_jury_new(request, pk):
    proposition = get_object_or_404(PropositionDissertation, pk=pk)
    count_proposition_role = PropositionRole.objects.filter(proposition_dissertation=proposition).count()
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    if proposition.author == adv or proposition.creator == adv.person:
        if request.method == "POST":
            form = ManagerPropositionRoleForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                status = data['status']
                adv = data['adviser']
                prop = data['proposition_dissertation']
                if status == "PROMOTEUR":
                    proposition.set_author(adv)
                    proposition_role.delete(status, prop)
                    proposition_role.add(status, adv, prop)
                elif count_proposition_role < 4:
                    proposition_role.add(status, adv, prop)
                return redirect('proposition_dissertation_detail', pk=proposition.pk)
            else:
                form = ManagerPropositionRoleForm(initial={'proposition_dissertation': proposition})
        else:
            form = ManagerPropositionRoleForm(initial={'proposition_dissertation': proposition})
        return layout.render(request, 'proposition_dissertations_jury_edit.html', {'form': form})
    else:
        return redirect('proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(is_teacher)
def proposition_dissertations_role_delete(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)
    proposition = prop_role.proposition_dissertation
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)

    if prop_role.status != 'PROMOTEUR' and (proposition.author == adv or proposition.creator == adv.person):
        prop_role.delete()

    return redirect('proposition_dissertation_detail', pk=proposition.pk)
