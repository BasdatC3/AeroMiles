from .auth import landing, login_view, register, logout_view, change_password
from .dashboard import dashboard
from .profile import profile
from .identity import (
    manage_identity, create_identity, edit_identity, delete_identity,
)
from .members import (
    manage_members, create_member, edit_member, delete_member,
)
from .partners import (
    manage_partners, partner_detail, create_partner, edit_partner, delete_partner,
)

__all__ = [
    'landing', 'login_view', 'register', 'logout_view', 'change_password',
    'dashboard',
    'profile',
    'manage_identity', 'create_identity', 'edit_identity', 'delete_identity',
    'manage_members', 'create_member', 'edit_member', 'delete_member',
    'manage_partners', 'partner_detail', 'create_partner', 'edit_partner', 'delete_partner',
]
