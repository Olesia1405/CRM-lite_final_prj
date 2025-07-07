from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone

class Company(models.Model):
    INN_LENGTH = 12

    INN = models.CharField(
        max_length=INN_LENGTH,
        validators=[MinLengthValidator(INN_LENGTH)],
        unique=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Storage(models.Model):
    address = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='storages'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.title} = {self.address}"


class Supplier(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='suppliers'
    )
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.company.title})'


class Product(models.Model):
    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
        related_name='products'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} (Остаток: {self.quantity})'


class Supply(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supplies'
    )
    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
        related_name='supplies'
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_supplies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Поставка #{self.id} от {self.supplier.name if self.supplier else 'неизвестного поставщика'}"


class SupplyProduct(models.Model):
    supply = models.ForeignKey(
        Supply,
        on_delete=models.CASCADE,
        related_name='supply_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='supply_products'
    )
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} x{self.quantity} в поставке #{self.supply.id}"


class Sale(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='sales'
    )
    buyer_name = models.CharField(
        max_length=255,
        verbose_name='Имя покупателя'
    )
    sale_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата продажи'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sales',
    )

    class Meta:
        verbose_name = 'Sale'
        ordering =  ['-sale_date']

    def __str__(self):
        return f'Продажа #{self.id} {self.buyer_name} ({self.sale_date.strftime("%d.%m.%Y")})'


class ProductSale(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='product_sales'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sales'
    )
    quantity = models.PositiveIntegerField(null=False, default=0, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"


class SalesReport(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    report_date = models.DateField()
    period = models.CharField(max_length=10, choices=[
        ('day', 'День'),
        ('week', 'Неделя'),
        ('month', 'Месяц'),
        ('year', 'Год'),
        ('custom', 'Пользовательский')
    ])
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'report_date']),
        ]
