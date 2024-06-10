import random
from faker import Faker
from django.core.management.base import BaseCommand
from tracker.models import Transaction, Category, User
fake = Faker()


class Command(BaseCommand):
    help = "Generate Transactions for testing"

    def handle(self, *args, **options):
        categories = [
            "Clothes",
            "Bills",
            'Food',
            "Medical",
            "Housing",
            "Salary",
            "Social",
            "Transport",
            "Housing"
        ]
        for category in categories:
            Category.objects.get_or_create(name=category)
        # get user
        user = User.objects.filter(username="admin").first()
        if not user:
            user = User.objects.create(
                username="admin", password="testing321#")
        categories = Category.objects.all()
        types = [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES]
        for i in range(20):
            Transaction.objects.create(
                user=user,
                category=random.choice(categories),
                amount=random.uniform(1, 2500),
                date=fake.date_between(start_date="-1y", end_date='today'),
                type=random.choice(types)
            )
