from shscripts.backup import setup_django
from pathlib import Path
from django.db import transaction
from django_src.apps.register.test_data.interest_themes import InterestThemeData
from django.db.models import ObjectDoesNotExist
from django.test import TestCase

# ./manage.py test --keepdb tests.test_transactions.TestTransactions
class TestTransactions(TestCase):
    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file
        setup_django(self.BASE_DIR)
        self.interest_themes_data = InterestThemeData()

    # ./manage.py test --keepdb tests.test_transactions.TestTransactions.test_nested_transactions
    def test_nested_transactions(self):
        """
        Test that if a nested transaction raises an exception the outer transaction is rolled back
        """

        # Whe catch the exception to continue with the assertions
        # Catching the exection in the most outer block its necessary to not hide the exception from django
        # so it can rollback the transaction
        try:
            with transaction.atomic():
                self.interest_themes_data.matematicas.save()
                with transaction.atomic():
                    self.interest_themes_data.programacion.save()
                    raise Exception("Error")
        except Exception:
            pass

        # save_data2 raises an execption so the data from save_data should not be saved

        # Check that the data was not saved
        with self.assertRaises(self.interest_themes_data.InterestTheme.DoesNotExist):
            self.interest_themes_data.InterestTheme.objects.get(name=self.interest_themes_data.matematicas.name)

    # ./manage.py test --keepdb tests.test_transactions.TestTransactions.test_nested_transactions_parent
    def test_nested_transactions_parent(self):
        """
        Test that if a parent transaction raises an exception the child transaction is rolled back
        """

        try:
            with transaction.atomic():
                self.interest_themes_data.matematicas.save()
                # Make a child transaction
                with transaction.atomic():
                    self.interest_themes_data.programacion.save()
                # programacion should be saved to db up to this point
                try:
                    self.interest_themes_data.InterestTheme.objects.get(name=self.interest_themes_data.programacion.name)
                except self.interest_themes_data.InterestTheme.DoesNotExist:
                    self.fail("programacion should have been saved to db")

                # Raise an exception in the parent transaction
                raise Exception("Error")
        except Exception:
            pass

        # programacion shouldn't be saved even do it was saved in the child transaction
        with self.assertRaises(self.interest_themes_data.InterestTheme.DoesNotExist):
            self.interest_themes_data.InterestTheme.objects.get(name=self.interest_themes_data.programacion.name)

        with self.assertRaises(self.interest_themes_data.InterestTheme.DoesNotExist):
            self.interest_themes_data.InterestTheme.objects.get(name=self.interest_themes_data.matematicas.name)
