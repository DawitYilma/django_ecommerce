from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/<slug:name>/', views.product, name="product"),
    path('register/', views.register, name='register'),
    path('customer_login/', views.customer_login, name='customer_login'),
    path('customer_logout/', views.customer_logout, name='customer_logout'),

    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order')
]