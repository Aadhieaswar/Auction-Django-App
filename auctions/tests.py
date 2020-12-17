from django.test import Client, TestCase

# import models
from .models import Listing, Bid, User

# Create your tests here.
class ListingTestCase(TestCase):
    # initial the sample / test database
    def setUp(self):

        # create a sample user
        user = User.objects.create(username="foo", password="baz", email="foo@baz.com")

        # create listings
        l1 = Listing.objects.create(name="dummy1", initial=100, category="Other")
        l2 = Listing.objects.create(name="dummy2", initial=200, category="Accessories")

        # create bids
        Bid.objects.create(user=user, listing=l1, highest_bid=110)
        Bid.objects.create(user=user, listing=l2, highest_bid=210)
        Bid.objects.create(user=user, listing=l1, highest_bid=130)

    # testing the database Models
    def test_bid_count(self):
        l = Listing.objects.get(initial=100)
        bids = Bid.objects.filter(listing=l).count()
        self.assertEqual(bids, 2)

    def test_valid_listing(self):
        l = Listing.objects.get(name="dummy1")
        self.assertTrue(l.is_valid_listing())

    def test_invalid_listing(self):
        l = Listing.objects.create(name="", initial=0)
        self.assertFalse(l.is_valid_listing())

    # testing the views / routs in the application
    def test_index_page(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
