from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('password/', views.change_password, name='change_password'),

    # Member - Identity
    path('identity/', views.manage_identity, name='identity'),
    path('identity/create/', views.create_identity, name='create_identity'),
    path('identity/<int:identity_id>/edit/', views.edit_identity, name='edit_identity'),
    path('identity/<int:identity_id>/delete/', views.delete_identity, name='delete_identity'),

    # Staff - Member Management
    path('members/', views.manage_members, name='manage_members'),
    path('members/create/', views.create_member, name='create_member'),
    path('members/<int:member_id>/edit/', views.edit_member, name='edit_member'),
    path('members/<int:member_id>/delete/', views.delete_member, name='delete_member'),

    # manage partners
    path('partners/', views.manage_partners, name='manage_partners'),
    path('partners/create/', views.create_partner, name='create_partner'),
    path('partners/<str:email>/detail/', views.partner_detail, name='partner_detail'),
    path('partners/<str:email>/edit/', views.edit_partner, name='edit_partner'),
    path('partners/<str:email>/delete/', views.delete_partner, name='delete_partner'),
]