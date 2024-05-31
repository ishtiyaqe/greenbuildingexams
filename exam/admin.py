from django.contrib import admin 
from django.utils.html import format_html
from .models import *



@admin.register(Pakage)
class PakageAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'old_price', 'image_tag','pdf', 'remove_pakage', 'on_homePage', 'best_selling', 'short_description', 'full_description', 'created_at']
    list_editable = ['price','old_price','on_homePage','remove_pakage','best_selling',]
    def short_description(self, obj):
        return obj.shor_des[:120] + '...' if len(obj.shor_des) > 60 else obj.shor_des
    short_description.short_description = 'Short Description'

    def full_description(self, obj):
        return obj.des[:120] + '...' if len(obj.des) > 60 else obj.des
    full_description.short_description = 'Full Description'

    def image_tag(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="50" height="50" />'.format(obj.main_image.url))
        return ''
    image_tag.short_description = 'Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Payment._meta.fields]

@admin.register(OrderPakage)
class OrderPakageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderPakage._meta.fields]

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Exam._meta.fields]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Answer._meta.fields]

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1  # Number of extra forms to display

@admin.register(Qestion)
class QestionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Qestion._meta.fields]
    inlines = [AnswerInline]

class affiliate_earningInline(admin.TabularInline):
    model = affiliate_earning
    extra = 1  # Number of extra forms to display

@admin.register(affiliate)
class affiliateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in affiliate._meta.fields]
    inlines = [affiliate_earningInline]