from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UniqueCode  # Import both properly
from django.utils import timezone
from datetime import timedelta


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)


# ❌ DO NOT DO THIS
# expired_codes = UniqueCode.objects.filter(...)

# ✅ Instead, define a method or view to access expired codes if needed
class UniqueCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'assigned_to', 'assigned_time', 'is_used')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def get_expired_codes(self):
        return UniqueCode.objects.filter(
            assigned_time__lt=timezone.now() - timedelta(days=7),
            is_used=False
        )

admin.site.register(UniqueCode, UniqueCodeAdmin)
