from django.db.models.functions import TruncDay, TruncWeek
from reportlab.pdfgen import canvas
from io import BytesIO
import matplotlib.pyplot as plt
from django.db.models import Sum, F
from .models import Sale, ProductSale

def generate_supply_pdf(supply):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 800, f'Накладная №{supply.id}')
    p.drawString(100, 700, f'Поставщик: {supply.supplier.name if supply.supplier else "-"}')
    p.drawString(100, 760, f'Дата: {supply.created_at.strftime("%d.%m.%Y")}')

    y = 700
    p.drawString(100, y, 'Товар')
    p.drawString(300, y, 'Кол-во')
    p.drawString(400, y, 'Цена')
    p.drawString(500, y, 'Сумма')

    for item in supply.supply_products.all():
        y -= 20
        p.drawString(100, y, item.product.title)
        p.drawString(300, y, str(item.quantity))
        p.drawString(400, y, str(item.price))
        p.drawString(500, y, str(item.quantity * item.price))

    p.drawString(400, y-40, f'ИТОГО: {supply.supply_products.aggregate(total=Sum(F("quantity") * F("price")))["total"]}')

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generate_sales_plot(company, date_from=None, date_to=None):
    plt.style.use('seaborn')

    sales = Sale.objects.filter(
        company=company,
        sale_date__range=[date_from, date_to]
    ) if date_from and date_to else Sale.objects.filter(company=company)

    sales_by_day = sales.annotate(
        day=TruncDay('sale_date')
    ).values('day').annotate(
        total=Sum('total_amount')
    ).order_by('day')

    top_products = ProductSale.objects.filter(
        sale__in = sales
    ).values(
        'product__title'
    ).annotate(
        total=Sum('quantity')
    ).order_by('-total')[:5]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

    days = [x['day'].strftime('%d.%m') for x in sales_by_day]
    amounts = [float(x['total']) for x in sales_by_day]

    ax1.bar(days, amounts, color='skyblue')
    ax1.set_title('продажи по дням')
    ax1.setylabel('сумма')
    ax1.grid(True)

    products = [x['product__title'][:15] for x in top_products]
    quantities = [x['total'] for x in top_products]

    ax2.bar(products, quantities, color='lightgreen')
    ax2.set_title('топ-5 товаров по количеству')
    ax2.grid(True)

    sales_by_week = sales.annotate(
        week=TruncWeek('sale_date')
    ).values('week').annotate(
        profit=Sum(F('product_sales__quantity') *
                   (F('product_sales__price') - F('product_sales__product__purchase_price')))
    ).order_by('week')

    weeks = [x['week'].strftime('%U') for x in sales_by_week]
    profits = [float(x['profit']) for x in sales_by_week]

    ax3.plot(weeks, profits, marker='o', color='salmon')
    ax3.set_title('прибыль по неделям')
    ax3.set_ylabel('прибыль')
    ax3.grid(True)

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf