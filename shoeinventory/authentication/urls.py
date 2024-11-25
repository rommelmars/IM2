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
    path('dashboard/', views.dashboard, name='dashboard'),  
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
    path('dashboard/api/', views.dashboard_api, name='dashboard_api'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)