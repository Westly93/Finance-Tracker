from django.db import models


class TransactionQuerySet(models.QuerySet):
    # get all the expenses transactions
    def get_expenses(self):
        return self.filter(type='expense')
    # get all the income transactions

    def get_income(self):
        return self.filter(type="income")
    # get the total of all the expenses otherwise zero

    def get_total_expenses(self):
        return self.get_expenses().aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    # get the total of all the incomes otherwise zero

    def get_total_income(self):
        return self.get_income().aggregate(
            total=models.Sum('amount')
        )['total'] or 0
