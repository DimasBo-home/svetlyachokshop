from django.db import models

from django.shortcuts import reverse

from django.utils.text import slugify
from transliterate import translit

from django.core.validators import MaxValueValidator, MinValueValidator

from decimal import Decimal
# Create your models here.

class Category(models.Model):
	name = models.CharField(max_length=50, verbose_name = 'Назва')
	slug = models.SlugField(blank=True,verbose_name="Ключове слово(не обов'ясково)")

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('category_list_url',kwargs={'slug':self.slug})

	def save(self, *args, **kwargs):
		if not self.slug and self.name:
			slug = slugify(translit(self.name,'uk', reversed=True))
			self.slug = slug
		super().save( *args, **kwargs)

	class Meta:
		verbose_name = 'Категорію'
		verbose_name_plural = 'Категорії'
		ordering = ['name']
		
class Page(models.Model):

	title = models.CharField(max_length=100, verbose_name='Заголовок')
	description = models.TextField(verbose_name='Опис')
	slug = models.SlugField(verbose_name="Ключове слово")

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('page_url', kwargs={'slug':self.slug})

	def get_edit_url(self):
		return reverse('page_edit_url', kwargs={'slug':self.slug})

	class Meta:
		verbose_name_plural = 'Сторінки сайта'
		verbose_name = 'Сторінку сайта'

def image_folder(instance, filename):
	filename = instance.slug + '.' + filename.split('.')[1]
	return "{0}/{1}".format(instance.slug,filename)

def image_folder_cover(instance, filename):
	filename = instance.slug + '_cover.' + filename.split('.')[-1]
	return "{0}/{1}".format(instance.slug,filename)

def image_folder_album(instance, filename):
	filename = instance.product.slug + '.' + filename.split('.')[-1]
	return "{0}/{1}".format(instance.product.slug, filename)

class Product(models.Model):

	title = models.CharField(max_length=50, verbose_name='Заголовок')
	description = models.TextField( verbose_name='Опис')
	price = models.DecimalField(max_digits=9, decimal_places=2,  verbose_name='Ціна')
	category = models.ForeignKey(Category,on_delete=models.CASCADE, verbose_name='Категорія')
	count = models.PositiveIntegerField(default=1,  verbose_name='Кількість товару')
	slug = models.SlugField(blank=True,  verbose_name="Ключове слово(не обов'ясково)")
	available = models.BooleanField(default=True, verbose_name='В наявності')
	date = models.DateTimeField(auto_now_add=True)
	album_cover = models.ImageField(upload_to=image_folder_cover, verbose_name='Фото обкладинки')

	def get_absolute_url(self):
		return reverse('product_detail_url',kwargs={'slug':self.slug})

	def get_add_order_url(self):
		return reverse('order_product_detail_url',kwargs={'slug':self.slug})

	def delete(self, *args, **kwargs):
		self.album_cover.delete(save=False)
		super().delete(args, kwargs)

	def save(self, *args, **kwargs):
		if not self.slug and self.title:
			slug = slugify(translit(self.title,'uk', reversed=True))
			self.slug = slug
		super().save( *args, **kwargs)

	def get_add_to_cart_url(self):
		return reverse('add_to_cart_url',kwargs={'slug':self.slug})

	def get_add_to_cart_order_url(self):
		return reverse('add_to_cart_url',kwargs={'slug':self.slug})

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'Продукт'
		verbose_name_plural = 'Продукти'
		ordering = ['-date']

class Reduction(models.Model):

	title = models.CharField(max_length = 100)
	reduction = models.PositiveSmallIntegerField(default = 1, validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ])
	description = models.TextField()
	product = models.ManyToManyField(Product)
	image = models.ImageField(upload_to=image_folder, blank=True, null=True)

	date = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return "{0}% | {1}".format(str(self.reduction), self.title)

	class Meta:
		verbose_name = 'Знишку'
		verbose_name_plural = 'Знишки'
		ordering = ['-date']

class ProductImage(models.Model):
	
	product = models.ForeignKey(Product, related_name='images',on_delete=models.CASCADE)
	images = models.ImageField(upload_to=image_folder_album )

	def __str__(self):
		return self.images.url

	def delete(self, *args, **kwargs):
		self.images.delete(save=False)
		super().delete(*args,**kwargs)

	class Meta:
		verbose_name = 'фото'
		verbose_name_plural = 'фото'

class CartItem(models.Model):

	product = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name='Продукт')
	qty = models.PositiveIntegerField(default=1,verbose_name='Назва')
	item_total = models.DecimalField(max_digits=9,decimal_places=2,default=0,blank=True,verbose_name="Сума(необов'язково, рахує самостійно)")

	def __str__(self):
		return "{0} Cart item for product {1}".format(self.id,self.product.title)

	def minus_qty(self):
		if self.qty > 1:
			self.qty -= 1
			self.item_total = self.qty * self.product.price
		self.save()
	
	
	def add_qty(self):
		if self.qty + 1 <= self.product.count:
			self.qty += 1
			self.item_total = self.qty * self.product.price
		self.save()

	def save(self, *args, **kwargs):
		if not self.item_total:
			self.item_total = self.qty * self.product.price 
		super().save( *args, **kwargs)

def sum_items(elements,save = True):
	total_price = Decimal(0.00)
	for item in elements:
		total_price = total_price + item.item_total
	return total_price

class Cart(models.Model):

	item = models.ManyToManyField(CartItem, blank=True)
	cart_total = models.DecimalField(max_digits=9,decimal_places=2,default=0)

	def __str__(self):
		return str(self.id)

	def add_to_cart(self,slug):
		product = Product.objects.get(slug=slug)
		new_item = CartItem.objects.get_or_create(product=product,item_total=product.price)[0]
		els = list(self.item.all())
		if new_item not in els:
			self.item.add(new_item)
			els.append(new_item)
#		print(els)
		self.set_sum(sum_items(els))


	def remove_product_cart(self,slug):
		product = Product.objects.get(slug=slug)
		els = list(self.item.all())
		for item in els:
			if item.product == product:
				self.item.remove(item)
				item.delete()
				els.remove(item)
#		print(els)
		self.set_sum(sum_items(els))

	def get_qty(self):
		return str(self.item.count())

	def set_sum(self,sum, save=True):
		self.cart_total = sum
		if save:
			self.save()

class Order(models.Model):
# Accepted in processing = AIP_status, 'Прийнятий в обробку'
# In processing = IP_status, 'В обробці'
# Paid = PAID_status, 'Оплачено'

	ORDER_STATUS_CHOICES = (
		('AIP_status', 'Прийнятий в обробку'),
		('IP_status', 'В обробці'),
		('PAID_status', 'Оплачено'),
	)

	DELIVERY_STATUS = (
		('nova_poshta', 'Нова пошта'),
		('ukr_poshta', 'Укр-пошта'),
	)
	# cart = models.ForeignKey(Cart,on_delete=models.CASCADE, verbose_name='Корзина')
	products = models.ManyToManyField(CartItem, verbose_name='Товари')
	total = models.DecimalField(max_digits=9, decimal_places=2, default = 0, verbose_name="Сума(необов'язково, рахує самостійно)",blank=True)
	second_name = models.CharField(max_length=200, verbose_name='Прізвище')
	first_name = models.CharField(max_length=200, verbose_name='Імя')
	last_name = models.CharField(max_length=200, verbose_name='Побатькові')
	phone_number = models.CharField(max_length=9, verbose_name='Номер телефону +380')
	email = models.EmailField(blank = True, verbose_name='Електрона пошта')
	buying_type = models.CharField(max_length=40,choices=DELIVERY_STATUS, verbose_name='Спосіб доставки')
	address = models.CharField(max_length=255, verbose_name='адреса')
	status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES,default='AIP_status', verbose_name='Статус')
	comments = models.TextField(blank = True, verbose_name='Коментарь')
	date = models.DateTimeField(auto_now_add=True)


	def get_admin_url(self):
		return reverse('order_detail_url',kwargs={'id':self.id})
	    
	def save(self, *args, **kwargs):
		super().save( *args, **kwargs)
		for item in self.products.all():
			if item.product.count - item.qty < 1:
				item.product.count = 0
				item.product.available = False
			else:
				item.product.count -= item.qty
			item.product.save()

	def add_product_order(self,item_id):
		C_item = CartItem.objects.get(id=item_id)
		els = list(self.products.all())
		for item in els:
			if item == C_item:
				item.add_qty()
				break
		self.set_sum(sum_items(els))

	def minus_product_order(self,item_id):
		C_item = CartItem.objects.get(id=item_id)
		els = list(self.products.all())
		for item in self.products.all():
			if item == C_item:
				item.minus_qty()
				break
		self.set_sum(sum_items(els))
	
	def delete(self, *args, **kwargs):
		for item in self.products.all():
			item.delete()
		super().delete(*args, **kwargs)

	def remove_product_order(self,item_id):
		C_item = CartItem.objects.get(id=item_id)
		els = list(self.products.all())
		for item in els:
			if item == C_item:
				self.products.remove(item)
				els.remove(item)
				break
		C_item.delete()
		self.set_sum(sum_items(els))

	def products_add(self,cart):
		self.save()
		for item in cart.item.all():
			new_item = CartItem(product=item.product,qty=item.qty,item_total=item.item_total)
			new_item.save()
			item.delete()
			self.products.add(new_item.id)
		self.save()
		cart.delete()

	def set_sum(self, sum,save = True):
		self.total = sum
		if save:
			self.save()

	def __str__(self):
		return "{} /ДАТА: {} /ПІБ: {} {} {}".format(str(self.id), str(self.date.strftime("%d-%B-%Y")), self.second_name,self.first_name, self.last_name)

	def get_absolute_url(self):
		return reverse('order_detail_url',kwargs={'id':self.id})

	def get_add_product_in_order(self):
		return reverse('add_product_in_order_url',kwargs={'id':self.id})

	class Meta:
		ordering = ['-date']
		verbose_name = 'Замовлення'
		verbose_name_plural = 'Замовлення'