from django.urls import path

from .views.auth import (
    landing, login_view, register, logout_view, change_password,
)
from .views.dashboard import dashboard
from .views.profile import profile
from .views.identity import (
    manage_identity, create_identity, edit_identity, delete_identity,
)
from .views.members import (
    manage_members, create_member, edit_member, delete_member,
)
from .views.partners import (
    manage_partners, partner_detail, create_partner, edit_partner, delete_partner,
)


urlpatterns = [
    path('', landing, name='landing'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('password/', change_password, name='change_password'),

    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),

    path('identity/', manage_identity, name='identity'),
    path('identity/create/', create_identity, name='create_identity'),
    path('identity/<str:identity_id>/edit/', edit_identity, name='edit_identity'),
    path('identity/<str:identity_id>/delete/', delete_identity, name='delete_identity'),

    path('members/', manage_members, name='manage_members'),
    path('members/create/', create_member, name='create_member'),
    path('members/<str:member_id>/edit/', edit_member, name='edit_member'),
    path('members/<str:member_id>/delete/', delete_member, name='delete_member'),

    path('partners/', manage_partners, name='manage_partners'),
    path('partners/create/', create_partner, name='create_partner'),
    path('partners/<str:email>/detail/', partner_detail, name='partner_detail'),
    path('partners/<str:email>/edit/', edit_partner, name='edit_partner'),
    path('partners/<str:email>/delete/', delete_partner, name='delete_partner'),
]
