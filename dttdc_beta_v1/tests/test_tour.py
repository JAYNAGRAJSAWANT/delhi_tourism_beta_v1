import pytest
from django.test import TestCase
from model_bakery import baker
from ebooking.models import DTTDCTour, DTTDCTourCategory


class TestTourCategoryCreation(TestCase):
    def setUp(self):
        self.dttdctourcategory = baker.make(DTTDCTourCategory)
        
    def test_create_tour_category(self):
        self.assertIsInstance(self.dttdctourcategory,DTTDCTourCategory)
        
        self.assertTrue(DTTDCTourCategory.objects.filter(id=self.dttdctourcategory.id).exists())
        