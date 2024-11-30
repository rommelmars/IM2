from django.contrib import admin
from django.urls import path, include
from .import views
from .views import inventory_list, add_shoe, update_shoe, delete_shoe, personal_information
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('profile/', views.profile_home, name='profile_home'), 
    path('inventory/', views.inventory, name='inventory'),  
    path('create_sale/', views.create_sale, name='create_sale'),
    path('categories/', views.categories, name='categories'),
    path('update_shoe/<int:shoe_id>/', update_shoe, name='update_shoe'),
    path('delete_shoe/<int:shoe_id>/', delete_shoe, name='delete_shoe'),
    path('', inventory_list, name='inventory_list'),
    path('add_shoe/', add_shoe, name='add_shoe'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('search/', views.search_products, name='search_products'),
    path('personal_information/', personal_information, name='personal_information'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),  # Logout URL
    path('admin_add_shoe/', views.admin_add_shoe, name='admin_add_shoe'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)