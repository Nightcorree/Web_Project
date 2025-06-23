# atelier/permissions.py

from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Разрешает доступ только владельцу объекта или администратору.
    """
    def has_object_permission(self, request, view, obj):
        # Администраторы могут делать всё
        if request.user.is_staff:
            return True
        # Владелец объекта может его редактировать/удалять
        return obj.user == request.user