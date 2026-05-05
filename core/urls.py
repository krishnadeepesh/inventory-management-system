from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin/add-manager/', views.admin_add_manager, name='admin_add_manager'),
    path('admin/managers/', views.admin_managers, name='admin_managers'),
    path('delete-manager/<int:manager_id>/', views.delete_manager, name='delete_manager'),
    
    # Manager
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/requests/', views.manager_requests, name='manager_requests'),
    path('manager/add-product/', views.add_product, name='add_product'),
    path('manager/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('manager/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('manager/add-category/', views.add_category, name='add_category'),
    path('manager/edit-category/<int:pk>/', views.edit_category, name='edit_category'),
    path('manager/delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    path('manager/process-request/<int:req_id>/<str:action>/', views.process_request, name='process_request'),
    
    # User
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/requests/', views.user_requests, name='user_requests'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Common
    path('feedback/<int:receiver_id>/', views.feedback, name='feedback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
