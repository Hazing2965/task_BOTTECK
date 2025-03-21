from django.db import models
from django.forms import ValidationError

# Create your models here.

    


class Categories(models.Model):
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class SubCategories(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    
class Product(models.Model):
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos/products/', blank=True, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategories, 
                                     on_delete=models.CASCADE)
    
    def clean(self):
        if self.sub_category.category != self.category:
            raise ValidationError('Подкатегория не принадлежит выбранной категории.')


    def __str__(self):
        return f'{self.category} - {self.sub_category} - {self.name}'
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    
class DistributionUser(models.Model):
    message = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    photo_id = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        if self.date:
            return f'{self.date.strftime("%d.%m.%Y %H:%M:%S %Z")}'
        else:
            return f'{self.date}'


class UsersBot(models.Model):
    user_id = models.BigIntegerField(primary_key=True)

    def __str__(self):
        return f'{self.user_id}'
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Cart(models.Model):
    user = models.ForeignKey(UsersBot, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()

    def __str__(self):
        return f'{self.user_id} - {self.product_id} - {self.count}'
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Orders(models.Model):
    user = models.ForeignKey(UsersBot, on_delete=models.CASCADE)
    order_data = models.JSONField()
    address = models.CharField(max_length=250)
    total_price = models.DecimalField(max_digits=100, decimal_places=2)
    paid = models.BooleanField(default=False)
    date_create = models.DateTimeField(auto_now_add=True)
    date_paid = models.DateTimeField(blank=True, null=True)
    

    def __str__(self):
        return f'{self.user_id} - {self.date_create.strftime("%d.%m.%Y %H:%M:%S %Z")}'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class Payments(models.Model):
    payment_id = models.CharField(max_length=250, primary_key=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    amount_net = models.DecimalField(max_digits=100, decimal_places=2)
    user = models.ForeignKey(UsersBot, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Orders, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user_id} - {self.amount}'
    
    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"









