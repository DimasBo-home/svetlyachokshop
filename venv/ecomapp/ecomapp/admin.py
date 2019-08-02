from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Product,ProductImage,Reduction ,Order, Page
from django_summernote.admin import SummernoteModelAdmin

def make_paid(modeladmin, request, queryset):
	queryset.update(status='PAID_status')
def make_ip(modeladmin, request, queryset):
	queryset.update(status='IP_status')
def make_aip(modeladmin, request, queryset):
	queryset.update(status='AIP_status')

make_aip.short_description = 'Помітити як Прийнятий в обробку'
make_ip.short_description = 'Помітити як В обробці'
make_paid.short_description = 'Помітити як Оплачено'

# cart = models.ForeignKey(Cart,on_delete=models.CASCADE, verbose_name='Корзина')
class OrderAdmin(admin.ModelAdmin):
#	fields = ('products',('second_name','first_name','last_name'), ('phone_number','email'),'buying_type','address','status','comments')
	list_filter = ['status']
	actions = [make_paid, make_aip, make_ip]

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(SummernoteModelAdmin,admin.ModelAdmin):
    fields = ('title','description','price','category',('count','available'),'slug')
    inlines = [ ProductImageInline, ]
    summernote_fields = ('description')

class PageAdmin(SummernoteModelAdmin):
    summernote_fields = ('description')

# Register your models here.
admin.site.register(Page, PageAdmin)
admin.site.register(Category)
# admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
# admin.site.register(Reduction)
admin.site.register(Product,ProductAdmin)