from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from ecomapp.models import Category, Product, Cart, CartItem, ProductImage, Order, Page
from django.core.paginator import Paginator

from django.http.response import HttpResponseRedirect
from ecomapp.forms import  OrderForm, PageEditForm, OrderForm, CategoryForm

from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin 
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from ecomapp.models import sum_items
# Create your views here.
def get_cart(request):
	try:
		cart_id = request.session['cart_id']
		cart = Cart.objects.get(id=cart_id)
		request.session['total'] = cart.item.count()
	except:
		cart = Cart()
		cart.save()
		cart_id = cart.id
		request.session['cart_id'] = cart_id
		cart = Cart.objects.get(id=cart_id)
	return cart

def delete_order_session(request):
	try:
		del(request.session['order_id'])
	except:
		print('not delete')
	try:
		del(request.session['cart_order_id'])
	except:
		print('not delete cart_order_id')
	try:
		del(request.session['order_total'])
	except:
		print('not delete order_total')
	return request

class BaseView(TemplateView):
	template_name = 'ecomapp/index.html'
	
	def get(self, request):
		request = delete_order_session(request)
		cart = get_cart(request)	
		categories = Category.objects.all() 
		lorem_ipsum = '''Lorem Ipsum - це текст-"риба", що використовується в друкарстві та дизайні. Lorem Ipsum є, фактично, стандартною "рибою" аж з XVI сторіччя, коли невідомий друкар взяв шрифтову гранку та склав на ній підбірку зразків шрифтів. "Риба" не тільки успішно пережила п'ять століть, але й прижилася в електронному верстуванні, залишаючись по суті незмінною. Вона популяризувалась в 60-их роках минулого сторіччя завдяки виданню зразків шрифтів Letraset, які містили уривки з Lorem Ipsum, і вдруге - нещодавно завдяки програмам комп'ютерного верстування на кшталт Aldus Pagemaker, які використовували різні версії Lorem Ipsum.'''
		try:
			description = Page.objects.get(slug='description')
		except:
			description = Page(title='Опис footer' , description= 'Опис про сайт',slug='description')
			description.save()
		
		try:
			about_us = Page.objects.get(slug='about-us')
		except:
			about_us = Page(title='Про нас' , description= lorem_ipsum,slug='about-us')
			about_us.save()
		
		try:
			contacts = Page.objects.get(slug='contacts')
		except:
			contacts = Page(title='Контакти', description= lorem_ipsum,slug='contacts')
			contacts.save()
		
		try:
			buying_type = Page.objects.get(slug='buying-type')
		except:
			buying_type = Page(title='Доставка', description= lorem_ipsum,slug='buying-type')
			buying_type.save()
		

		self.context = {
			'categories': categories,
			'cart':cart,
			'description':description,
			'buying_type':buying_type,
			'about_us':about_us,
			'contacts':contacts,
		}
		return render(request,self.template_name,context=self.context)

class OrderDetailView(BaseView):

	template_name = 'ecomapp/order_detail.html'
	def get(self, request,id):
		super().get(request)
		order = Order.objects.get(id=id)
		self.context['form'] = OrderForm(instance = order)
		self.context['order'] = order
		return render(request,self.template_name,context=self.context)

	def post(self, request, id):
		super().get(request)
		order = Order.objects.get(id=id)
		bound_form = OrderForm(request.POST, instance=order)
		self.context['form'] = bound_form
		self.context['order'] = order
		if bound_form.is_valid():
			form = bound_form.save()
		return render(request,self.template_name,context=self.context)

class PageView(BaseView):

	template_name = 'ecomapp/page.html'

	def get(self,request,slug):
		super().get(request)
		self.context['page'] = Page.objects.get(slug=slug)
		return render(request, self.template_name, context=self.context)

class PageEdit(LoginRequiredMixin,BaseView):
	template_name = 'ecomapp/page_edit.html'
	
	raise_exception = True

	def get(self, request,slug):
		super().get(request)
		page = Page.objects.get(slug=slug)
		self.context['form'] = PageEditForm(instance = page)
		self.context['page'] = page
		return render(request,self.template_name,context=self.context)

	def post(self,request,slug):
		super().get(request)
		self.context['page'] = Page.objects.get(slug=slug)
		bound_form = PageEditForm(request.POST, instance=self.context['page'])
		self.context['form'] = bound_form
		if bound_form.is_valid():
			form = bound_form.save()
			return redirect(reverse('page_url', kwargs={'slug':form.slug}))
		return render(request,self.template_name,context=self.context)

class IndexView(BaseView):

	def get(self,request):
		super().get(request)
		products = Product.objects.filter(available=True)
		#масив для вюшки з категорією на головній і її продуктами
		categories_index = []
		for category in self.context['categories']:
			p = products.filter(category=category)
			if len(p) > 0:
				c = {
					'name':category.name,
					'url':category.get_absolute_url(),
					'products':p[:3]
				}
				categories_index.append(c)
		self.context['categories_index'] = categories_index
		return render(request,self.template_name,context=self.context)

class SearchView(BaseView):

	template_name = 'ecomapp/product_list.html'
	def get(self,request):
		super().get(request)
		search_query = request.GET.get('search', '')
		if search_query == '':
			return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
		self.context['category'] = Category()
		self.context['category'].name = 'Пошук: ' + search_query
		products = Product.objects.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) )
		paginator = Paginator(products, 9)
		page_number = request.GET.get('page', 1)
		page = paginator.get_page(page_number)
		self.context['page'] = page
		return render(request,self.template_name,context=self.context)

class CategoryView(BaseView):

	template_name = 'ecomapp/product_list.html'
	def get(self,request,slug):
		super().get(request)		
		self.context['category'] = self.context['categories'].get(slug=slug)
		self.context['category'].name = 'Категорія: ' + self.context['category'].name 
		products = Product.objects.filter(category=self.context['category'])
		paginator = Paginator(products, 9)
		page_number = request.GET.get('page', 1)
		page = paginator.get_page(page_number)
		self.context['page'] = page
		self.context['is_paginated'] = page.has_other_pages()

		if page.has_previous():
			self.context['prev_url'] = '?page={}'.format(page.previous_page_number())
		else:
			self.context['prev_url'] = False

		if page.has_next():
			self.context['next_url'] = '?page={}'.format(page.next_page_number())
		else:
			self.context['next_url'] = False
		return render(request, self.template_name ,context=self.context)

class CategoriesEditView(LoginRequiredMixin,BaseView):
	template_name = 'ecomapp/edit_categories.html'
	
	raise_exception = True

	def get(self,request):
		super().get(request)
		self.context['form'] = CategoryForm()
		return render(request,self.template_name,context=self.context)

	def post(self,request):
		super().get(request)
		self.context['form'] = CategoryForm()
		bound_form = CategoryForm(request.POST)
		if bound_form.is_valid():
			form = bound_form.save()
			self.context['categories'] = Category.objects.all()
			return render(request,self.template_name,context=self.context)			
		return render(request,self.template_name,context=self.context)		

class ProductDetailView(BaseView):

	template_name = 'ecomapp/product_detail.html'
	def get(self,request,slug):
		super().get(request)		
		self.context['product'] = Product.objects.get(slug=slug)
		self.context['product_album'] = ProductImage.objects.filter(product=self.context['product'])
		return render(request, self.template_name ,context=self.context)

#order views
def remove_product_order(request,id, item_id):
	order = Order.objects.get(id=id)
	order.remove_product_order(item_id)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def add_product_order(request,id, item_id):
	order = Order.objects.get(id=id)
	order.add_product_order(item_id)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def minus_product_order(request,id, item_id):
	order = Order.objects.get(id=id)
	order.minus_product_order(item_id)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def get_cart_order(request):
	try:
		cart_order_id = request.session['cart_order_id']
		cart = Cart.objects.get(id=cart_order_id)
		request.session['order_total'] = cart.item.count()
	except:
		cart = Cart()
		cart.cart_total = Order.objects.get(id=request.session['order_id']).total
		cart.save()
		cart_order_id = cart.id
		request.session['cart_order_id'] = cart_order_id
		cart = Cart.objects.get(id=cart_order_id)
	return cart

class OrderProductDetailView(TemplateView):
	template_name = 'ecomapp/order_product_detail.html'

	def get(self,request,slug):
		product = Product.objects.get(slug=slug)
		cart_order = get_cart_order(request)
		context = {
		'product' :product ,
		'cart_order':cart_order,
		'product_album' : ProductImage.objects.filter(product=product),
		'categories':  Category.objects.all()
		}
		return render(request, self.template_name ,context=context)

class OrderIndexView(TemplateView):
	template_name = "ecomapp/order_index.html"
	def get(self,request):
		cart_order = get_cart_order(request)
		search_query = request.GET.get('search', '')
		if search_query != '':
			title = 'Пошук'
			products = Product.objects.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) )
		else:
			title = 'всі продукти.'
			products = Product.objects.all()
		context = {
			'cart_order' : cart_order,
			'categories' : Category.objects.all(),
			'products' : products,
			'title': title
		}
		return render(request, self.template_name ,context=context)

class OrderCategoryView(TemplateView):
	template_name = "ecomapp/order_index.html"
	context = {}
	def get(self,request, slug):
		cart_order = get_cart_order(request)
		self.context['cart_order'] = cart_order
		self.context['categories'] = Category.objects.all()
		category = self.context['categories'].filter(slug=slug)
		self.context['products'] = Product.objects.filter(category=category)
		return render(request, self.template_name ,context=self.context)


class OrderCartView(TemplateView):
	template_name = "ecomapp/order_cart.html"
	context = {}
	def get(self, request):
		cart_order = get_cart_order(request)
		self.context['cart_order'] = cart_order
		self.context['categories'] = Category.objects.all()
		return render(request, self.template_name ,context=self.context)

def add_product_in_order(request,id):
	order = Order.objects.get(id=id)
	request.session['order_id'] = id
	cart = get_cart_order(request)
	for item in cart.item.all():
		cart.item.remove(item)
	for item in order.products.all():
		cart.item.add(item.id)
	cart.save()
	return redirect(reverse('add_order_index_url'))

def save_order(request):
	cart_order = get_cart_order(request)
	id = request.session['order_id']
	order = Order.objects.get(id=id)
	if order.products.count() > 0:
		for item in order.products.all():
			cart_order.item.remove(item)
	for item in cart_order.item.all():
		order.products.add(item)
	order.set_sum(cart_order.cart_total)
	request = delete_order_session(request)
	return redirect(reverse('order_detail_url',kwargs={'id':id}))

class CreateOrder(BaseView):
	template_name = 'ecomapp/order.html'
	
	def send_order(self, order):
		email = settings.EMAIL_HOST_USER
		message = '''{} {} {}<br>
Сума: {}<br>
Номер: {}<br>c
<a href="#">переглянути </a>'''.format(order.second_name, order.first_name, order.last_name, order.total, order.phone_number)
		tema = 'Замовлення !!!'
		try:
			print('yessssssssssssssss!!!!!!!!')
			send_mail(tema, message, email, [email] ,html_message=message, fail_silently=False)
		except:
			print('email error!!!!!!!!!!!!!!!!!!!!!!!!!')

	def get(self,request):
		super().get(request)
		self.context['form'] = OrderForm()
		return render(request, self.template_name, context=self.context )

	def post(self,request):
		super().get(request)
		bound_form = OrderForm(request.POST)
		if bound_form.is_valid():
			form = bound_form.save(commit=False)
			form.total = self.context['cart'].cart_total
			form.products_add(self.context['cart'])
			try:
				self.send_order(form)
			except:
				print("not network") 	
			return redirect(reverse('order_finish_url'))
		self.context['form'] = bound_form 
		return render(request, self.template_name, context=self.context )

class OrderFinish(BaseView):

	template_name = 'ecomapp/order_finish.html'
# cart views
class CartView(BaseView):

	template_name = 'ecomapp/cart.html'

def add_to_cart(request, slug):
	try:
		if request.session['order_id']:
			cart = get_cart_order(request)
	except:
		cart = get_cart(request)
	
	flug = False
	product = Product.objects.get(slug=slug)
	els = list(cart.item.all())
	for item in els:
		if item.product == product:
			item.add_qty()
			flug = True
			cart.set_sum(sum_items(els))
			break
	if flug==False:
		cart.add_to_cart(slug)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def minus_to_cart(request, slug):
	try:
		if request.session['order_id']:
			cart = get_cart_order(request)
	except:
		cart = get_cart(request)
	product = Product.objects.get(slug=slug)
	els = list(cart.item.all())
	for item in els:
		if item.product ==  product:
			item.minus_qty()
			cart.set_sum(sum_items(els))
			break
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def remove_from_view(request, slug):
	try:
		if request.session['order_id']:
			cart = get_cart_order(request)
	except:
		cart = get_cart(request)
	cart.remove_product_cart(slug)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
