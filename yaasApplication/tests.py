from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .models import auction


# Create your tests here.

class createAuction(TestCase):
    # UC3 Create Auction
    # UC6  Bid
    # UC10 Concurrency

    def testCreateAuction(self):
        self.user1 = User.objects.create(username="test1", password="test2", email="test@gmail.com").save()

        client = Client()
        response = client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        response = client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username="test1", password="test2")
        client.get(reverse('create_auction'))

        numberAuction = auction.objects.count()

        response = self.client.post(reverse)

    def bidAuction(self):
        print("fill in later")

    def bidAuction_concurrency(self):
        print("fill in later")
