import pytest
from django.test import TestCase
from model_bakery import baker
from django.db import IntegrityError
from django.utils import timezone
from ebooking.models import DTTDCTour, DTTDCTourCategory

### ADDING TEST CASES BY ABHIJEET THORAT ####

class TestTourCategoryCreation(TestCase):
    def setUp(self):
        self.dttdctourcategory = baker.make(DTTDCTourCategory)
        
    def test_create_tour_category(self):
        self.assertIsInstance(self.dttdctourcategory,DTTDCTourCategory)
        
        self.assertTrue(DTTDCTourCategory.objects.filter(id=self.dttdctourcategory.id).exists())

    def test_category_str_returns_name(self):
        category = baker.make(DTTDCTourCategory, category_name="City Tours")
        self.assertEqual(str(category),"City Tours")
        
    def test_category_name_unique(self):
        category_name = "Unique Tour Category"
        baker.make(DTTDCTourCategory,category_name=category_name)
        
        with self.assertRaises(IntegrityError):
            DTTDCTourCategory.objects.create(category_name=category_name)
    
    def test_category_image_is_optional(self):
        category_none = baker.make(DTTDCTourCategory,category_image=None)
        self.assertIsNone(category_none.category_image)
        
        category_blank = baker.make(DTTDCTourCategory, category_image='')
        self.assertEqual(category_blank.category_image,'')
        
class TestDTTDCTourModel(TestCase):
    def setUp(self):
        self.category = baker.make(DTTDCTourCategory, category_name="Day Tours")
        
    def test_create_tour_with_required_fields(self):
        tour = baker.make(
            DTTDCTour,
            tour_category=self.category,
            fare_adult="300.00",
            fare_child="300.00",
        )
        
        self.assertIsInstance(tour,DTTDCTour)
        self.assertTrue(DTTDCTour.objects.filter(id=tour.id).exists())
        
    def test_create_tour_with_required_fields_without_baker(self):
        tour = DTTDCTour.objects.create(
            tour_category=self.category,
            fare_adult="300.00",
            fare_child="300.00"
        )
        self.assertIsInstance(tour,DTTDCTour)
        self.assertTrue(DTTDCTour.objects.filter(id=tour.id).exists())
        
    def test_tour_name_is_required(self):
        with self.assertRaises(IntegrityError):
            DTTDCTour.objects.create(
                tour_category=self.category,
                fare_adult="300.00",
                fare_child="300.00",
                tour_name=None
            )
            
    def test_tour_str_returns_name(self):
        tour = baker.make(
            DTTDCTour,
            tour_name="Delhi Tour City",
            tour_category=self.category,
            fare_adult="1000.00",
            fare_child="500.00",
            )
        
        self.assertEqual(str(tour),"Delhi Tour City")
    
    # def test_tour_fare_are_required(self):
    #     with self.assertRaises(IntegrityError):
    #         DTTDCTour.objects.create(
    #             tour_name="Invalid Tour",
    #             tour_category=self.category,
    #             fare_adult="100.00",
    #             fare_child="50.00",
    #         )

    #     # fare_child is required
    #     with self.assertRaises(IntegrityError):
    #         DTTDCTour.objects.create(
    #             tour_name="Invalid Tour 2",
    #             tour_category=self.category,
    #             fare_adult="100.00",
    #             fare_child="50.00",
    #         )
    
    def test_realted_name_tours_on_category(self):
        tour1 = baker.make(
            DTTDCTour,
            tour_category=self.category,
            fare_adult="100.00",
            fare_child="50.00",
        )
        
        tour2 = baker.make(
            DTTDCTour,
            tour_category=self.category,
            fare_adult="200.00",
            fare_child="100.00",
        )
        
        related_qs = self.category.tours.all()
        self.assertIn(tour1,related_qs)
        self.assertIn(tour2,related_qs)
        self.assertEqual(related_qs.count(),2)
    
    def test_created_at_is_auto_populated(self):
        tour = baker.make(
            DTTDCTour,
            tour_category=self.category,
            fare_adult="500.00",
            fare_child="250.00",
        )
        self.assertIsNotNone(tour.created_at)
        self.assertLessEqual(tour.created_at, timezone.now())