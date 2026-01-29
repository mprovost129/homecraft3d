from django.test import TestCase, Client
from django.urls import reverse
from products.models import Category, Product
from sellers.models import Seller
from django.contrib.auth import get_user_model

class StorefrontCategoryFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.seller = Seller.objects.create(user=self.user)
        self.parent_cat = Category.objects.create(name='ParentCat', position=1)
        self.sub_cat = Category.objects.create(name='SubCat', parent=self.parent_cat, position=2)
        self.other_cat = Category.objects.create(name='OtherCat', position=3)
        self.prod1 = Product.objects.create(name='Prod1', description='desc', seller=self.seller, price=10, category=self.parent_cat, is_physical=True, featured_manual=True)
        self.prod2 = Product.objects.create(name='Prod2', description='desc', seller=self.seller, price=20, category=self.sub_cat, is_physical=True, featured_manual=True)
        self.prod3 = Product.objects.create(name='Prod3', description='desc', seller=self.seller, price=30, category=self.other_cat, is_physical=True, featured_manual=True)

    def test_filter_by_parent_category(self):
        url = reverse('storefront_home') + f'?category={self.parent_cat.id}'
        response = self.client.get(url)
        self.assertContains(response, 'Prod1')
        self.assertContains(response, 'Prod2')
        self.assertNotContains(response, 'Prod3')

    def test_filter_by_subcategory(self):
        url = reverse('storefront_home') + f'?subcategory={self.sub_cat.id}'
        response = self.client.get(url)
        self.assertNotContains(response, 'Prod1')
        self.assertContains(response, 'Prod2')
        self.assertNotContains(response, 'Prod3')

    def test_no_filter_shows_all(self):
        url = reverse('storefront_home')
        response = self.client.get(url)
        self.assertContains(response, 'Prod1')
        self.assertContains(response, 'Prod2')
        self.assertContains(response, 'Prod3')
