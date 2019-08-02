from django.urls import path, include
from ecomapp import views

urlpatterns = [
	path('',views.IndexView.as_view(), name='index'),
#prodicts url
	path('search/',views.SearchView.as_view(), name = 'search'),
	path('product/<str:slug>', views.ProductDetailView.as_view(),name='product_detail_url'),

#pages url
	path('page/<str:slug>', views.PageView.as_view() , name='page_url'),
	#edit	
	path('page_edit/<str:slug>', views.PageEdit.as_view() , name='page_edit_url'),
#orders url
	path('order/', views.CreateOrder.as_view(),name='create_order_url'),
	path('orders/', views.ListOrder.as_view(),name='order_list_url'),
	path('order/show/<int:id>', views.OrderDetailView.as_view(),name='order_detail_url'),
	#add product in order
	path('order/add/product/order=<int:id>', views.add_product_in_order,name='add_product_in_order_url'),
	path('order/add_product/category/<str:slug>', views.OrderCategoryView.as_view(), name='add_order_category_url'),
	path('order/add_product', views.OrderIndexView.as_view(), name='add_order_index_url'),
	path('order/add/cart/', views.OrderCartView.as_view(),name='order_cart_url'),
	path('order/add/save/', views.save_order, name='save_order_url'),
	path('order/add/product/<str:slug>',views.OrderProductDetailView.as_view(),name='order_product_detail_url'),
#	path('order/cart/add/<str:slug>', views.add_to_order_cart,name='add_order_to_cart_url'),
	
	#edit 	
	path('order/remove/<int:id>/<int:item_id>',views.remove_product_order,name='remove_product_order_url'),
	path('order/add/<int:id>/<int:item_id>', views.add_product_order,name='add_product_order_url'),
	path('order/minus/<int:id>/<int:item_id>', views.minus_product_order ,name='minus_product_order_url'),

	path('order_finish/',views.OrderFinish.as_view(), name='order_finish_url'),
#carts url
	path('cart/', views.CartView.as_view(),name='cart_url'),
	#edit	
	path('cart/minus/<str:slug>',views.minus_to_cart,name='minus_to_cart_url'),
	path('cart/add/<str:slug>',views.add_to_cart,name='add_to_cart_url'),
	path('cart/remove/<str:slug>',views.remove_from_view,name='remove_from_view_url'),

#categories url
	path('category/<str:slug>',views.CategoryView.as_view(), name='category_list_url' ),
	#edit	
	path('edit_categories/',views.CategoriesEditView.as_view(),name='edit_categories_url'),
]
