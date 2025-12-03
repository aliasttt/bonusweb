from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Business, Customer, Product, Wallet, Transaction, Slider, ImageCache


class BusinessAdminForm(forms.ModelForm):
    """Custom form for Business admin with password field handling"""
    password_display = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password to change'}),
        required=False,
        help_text="Leave empty to keep current password. Enter new password to change it."
    )
    
    class Meta:
        model = Business
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Show password status instead of actual password
            if self.instance.has_password():
                self.fields['password_display'].help_text = "Password is set. Enter new password to change it."
            else:
                self.fields['password_display'].help_text = "No password set. Enter password to set one."
    
    def save(self, commit=True):
        business = super().save(commit=False)
        password_display = self.cleaned_data.get('password_display')
        
        if password_display:
            business.set_password(password_display)
        
        if commit:
            business.save()
        return business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    form = BusinessAdminForm
    list_display = ("id", "name", "owner", "phone", "password_status", "created_at")
    list_filter = ("created_at", "owner")
    search_fields = ("name", "phone", "owner__username")
    readonly_fields = ("created_at", "password_status")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("owner", "name", "description")
        }),
        ("Contact Information", {
            "fields": ("phone", "address", "website")
        }),
        ("Security", {
            "fields": ("password_display", "password_status"),
            "description": "Password is used for in-person business access. It's securely hashed and never displayed."
        }),
        ("Business Settings", {
            "fields": ("reward_point_cost",)
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )
    
    def password_status(self, obj):
        """Display password status instead of actual password"""
        if obj.has_password():
            return format_html('<span style="color: green;">✓ Password Set</span>')
        else:
            return format_html('<span style="color: red;">✗ No Password</span>')
    password_status.short_description = "Password Status"
    
    def get_readonly_fields(self, request, obj=None):
        """Make password field readonly in list view"""
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing existing object
            readonly_fields.append('password')  # Hide the actual password field
        return readonly_fields


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "business", "active")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "business", "points_balance", "reward_point_cost")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "amount", "created_at")


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ("id", "store", "business", "is_active", "order", "created_at")
    list_filter = ("is_active", "created_at", "business")
    search_fields = ("store", "address", "description")
    list_editable = ("is_active", "order")
    ordering = ("order", "-created_at")


@admin.register(ImageCache)
class ImageCacheAdmin(admin.ModelAdmin):
    list_display = ("id", "content_type", "object_id", "original_path", "has_data_display", "file_size_display", "created_at", "last_accessed")
    list_filter = ("content_type", "created_at", "last_accessed")
    search_fields = ("original_path", "content_type", "object_id")
    readonly_fields = ("created_at", "updated_at", "last_accessed", "has_data_display", "image_preview")
    ordering = ("-last_accessed", "-created_at")
    
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("content_type", "object_id", "original_path")
        }),
        ("داده تصویر", {
            "fields": ("image_url", "image_data", "content_type_header", "file_size")
        }),
        ("پیش‌نمایش", {
            "fields": ("has_data_display", "image_preview")
        }),
        ("زمان‌ها", {
            "fields": ("created_at", "updated_at", "last_accessed")
        }),
    )
    
    def has_data_display(self, obj):
        """نمایش وضعیت داده"""
        if obj.has_data:
            if obj.image_data:
                return format_html('<span style="color: green;">✓ Base64 ({:.1f} KB)</span>', len(obj.image_data) / 1024)
            elif obj.image_url:
                return format_html('<span style="color: blue;">✓ URL</span>')
        return format_html('<span style="color: red;">✗ No Data</span>')
    has_data_display.short_description = "وضعیت داده"
    
    def file_size_display(self, obj):
        """نمایش حجم فایل"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "-"
    file_size_display.short_description = "حجم فایل"
    
    def image_preview(self, obj):
        """پیش‌نمایش تصویر"""
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.image_url)
        elif obj.image_data:
            # نمایش base64
            data_url = f"data:{obj.content_type_header or 'image/jpeg'};base64,{obj.image_data[:100]}..."
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', data_url)
        return "بدون تصویر"
    image_preview.short_description = "پیش‌نمایش"


