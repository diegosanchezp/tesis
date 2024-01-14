from typing import cast
from datetime import date, timedelta
from pathlib import Path


from django.http.response import HttpResponse
from django.urls.base import reverse_lazy
from django.template import loader
from django.db import models

from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator

from .test_utils import TestCaseWithData
from django.conf import settings
from .models import (
    Mentor, Student,
    RegisterApprovals,
    RegisterApprovalStates, RegisterApprovalEvents,
)
from .forms import (
    ApprovalsFilterForm
)

from . import approvals_view

# ./manage.py test --keepdb django_src.apps.register.test_approvals.TestApprovals
class TestApprovals(TestCaseWithData):
    def setUp(self):
        super().setUp()
        self.url = reverse_lazy("approvals")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # The data that I'll need
        # Created student with status
        # Created mentor with status


        cls.mentor = Mentor.objects.create(
            user=cls.mentor_user,
            carreer=cls.computacion,
            voucher=SimpleUploadedFile(
                name="mentor_voucher.pdf", content=b"file_content",
                content_type="application/pdf"
            ),
        )

        cls.student_type = ContentType.objects.get_for_model(Student)
        cls.student.voucher = SimpleUploadedFile(
            name="profile_pic.jpg",
            content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
            content_type="image/jpeg",
        )

        cls.student.save()

        cls.mentor_type = ContentType.objects.get_for_model(Mentor)

        cls.mentor_approval = RegisterApprovals.objects.create(
            user=cls.mentor_user,
            user_type=cls.mentor_type,
            admin=cls.admin_user, # approved by the admin
            state=RegisterApprovalStates.WAITING,
        )

    # ./manage.py test --keepdb django_src.apps.register.test_approvals.TestApprovals.test_form_valid
    def test_form_valid(self):
        form = ApprovalsFilterForm(
            data={
                "approvals": [self.mentor_approval.pk],
                "action": RegisterApprovalEvents.APPROVE,
            }
        )
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["approvals"].count(), 1)


    # ./manage.py test --keepdb django_src.apps.register.test_approvals.TestApprovals.test_form_invalid
    def test_form_invalid(self):
        """
        Test that it validates that the users exist
        """
        form = ApprovalsFilterForm(
            data={
                "approvals": [self.mentor_approval.pk, self.student_approval.pk],
                "action": RegisterApprovalEvents.APPROVE,
                "status": RegisterApprovalStates.WAITING,
            }
        )

        # Form should be invalid because you cant approve a user that is already approved,
        # the student is already approved
        self.assertFalse(form.is_valid(), msg=form.errors)
        self.assertIn("approvals", form.fields)
        self.assertEqual(form.cleaned_data["approvals"].count(), 2)
        self.assertIn("__all__", form.errors)
        self.assertEqual(len(form.errors["__all__"]), 1)
        print(form.errors)

    # ./manage.py test --keepdb django_src.apps.register.test_approvals.TestApprovals.test_model
    def test_model(self):

        self.assertEqual(self.mentor_approval.user_type, self.mentor_type, msg=self.mentor_approval.user_type)
        self.assertEqual(self.mentor_approval.user, self.mentor_user)

        mentors_approvals = RegisterApprovals.objects.filter(user_type__model="mentor")
        self.assertEqual(mentors_approvals.count(), 1)

        self.assertEqual(self.student_approval.user_type, self.student_type, msg=self.student_approval.user_type)
        self.assertEqual(self.student_approval.user, self.student_user)

        students_approvals = RegisterApprovals.objects.filter(user_type__model="student")
        self.assertGreaterEqual(students_approvals.count(), 1)

    # ./manage.py test --keepdb django_src.apps.register.test_approvals.TestApprovals.test_filter_users
    def test_filter_users(self):

        #?page=1&status=approved
        data = {
            "status": RegisterApprovalStates.APPROVED,
            "action" :"search",
            "page": 1,
        }

        self.assertIsNotNone(self.url)

        request = RequestFactory().post(
            path=self.url,
            data=data,
        )

        # mock htmx
        request.htmx = True

        context = approvals_view.filter_users(request)

        filter_form = context["filter_form"]

        # Check forms
        self.assertTrue(isinstance(filter_form, ApprovalsFilterForm))
        self.assertTrue(filter_form.is_valid(), msg=filter_form.errors)
        self.assertEqual(filter_form.cleaned_data["status"], RegisterApprovalStates.APPROVED)

        # Check returned paginated data
        self.assertIn("page_obj", context)
        self.assertIn("search_query_params", context)
        self.assertEqual(context["search_query_params"], f"status={data['status']}")


        page_obj: Paginator = context["page_obj"]

        for approval in page_obj.object_list:
            self.assertEqual(approval.state, RegisterApprovalStates.APPROVED)
            self.assertEqual(approval.user_type.model, self.student_type.model)

        response = cast(HttpResponse, approvals_view.approvals_view(request))
        response_html = response.content.decode()

    # ./manage.py test --keepdb django_src.apps.register.test_approvals.TestApprovals.test_update_approval
    def test_update_approval(self):

        # - [ ] Check if the filters are kept
        # - [ ] What should be default filters ? None ?

        # Login the admin user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.admin_user, password="dev123456",
        ))

        data = {
            "page": 1,
            "approvals": [self.mentor_approval.pk],
            "action": RegisterApprovalEvents.REJECT,
        }

        response = self.client.post(
            path=self.url,
            data=data,
            # mock htmx
            headers={"HX-Request": "true"},
        )

        request = response.wsgi_request


        # We test that the form is invalid, because the Approval should in the REJECTED state due to
        # the post request above
        form = approvals_view.get_approvals_form(request)
        self.assertFalse(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["approvals"].count(), 1)
        self.assertEqual(form.cleaned_data["action"], RegisterApprovalEvents.REJECT)

        self.assertEqual(approvals_view.get_page_number(request), data["page"])

        #  Check if it transitioned the state to REJECTED
        self.assertEqual(
            RegisterApprovals.objects.get(user=self.mentor_user).state,
            RegisterApprovalStates.REJECTED
        )

        response_html = response.content.decode()

        # I should be careful with this, it might not appear because of the pagination
        self.assertIn(RegisterApprovalStates.REJECTED, response_html)

        print(response_html)


    def tearDown(self):
        # Cleanup action remove the voucher
        self.student.voucher.delete()
        self.mentor.voucher.delete()

