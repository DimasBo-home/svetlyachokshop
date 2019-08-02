# -*- coding: utf-8 -*-
from django import forms
from django.utils import timezone
from ecomapp.models import Order, Page, Category
from django_summernote.widgets import SummernoteWidget

class PageEditForm(forms.ModelForm):
	class Meta:
		model = Page
		fields = ['description']
		widgets = {
			'description' : SummernoteWidget(),
		}

class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ['name']

class OrderForm(forms.ModelForm):

	class Meta:
		model = Order
		fields = ['second_name','first_name','last_name','phone_number','email','buying_type','address','comments']
		labels = {
			"email": "електрона пошта(необов'ясково, для підписки на вигідні пропозиції)"
		}
