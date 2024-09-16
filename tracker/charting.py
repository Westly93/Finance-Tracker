import plotly.express as px
from django.db.models import Sum
from .models import Category

def income_expenses_bar(qs):
    x_vals= ["Income", "Expenses"]
    total_income= qs.filter(type='income').aggregate(
        total= Sum("amount")
    )['total']
    total_expenses= qs.filter(type='expense').aggregate(
        total= Sum("amount")
    )['total']

    fig= px.bar(x=x_vals, y=[total_income, total_expenses])
    return fig


def category_pie_chart(qs):
    count_per_category= qs.order_by('category').values('category').annotate(
        total= Sum('amount')
    )

    category_pks= count_per_category.values_list('category', flat= True).order_by('category')
    categories= Category.objects.filter(pk__in= category_pks).order_by('pk').values_list('name', flat=True)
    total_amounts= count_per_category.values_list('total', flat= True)
    fig= px.pie(values= total_amounts, names= categories)
    fig.update_layout(title_text= 'Total Contribution based on category')
    return fig