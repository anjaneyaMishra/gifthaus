from django.contrib import admin
#from django_summernote.admin import SummernoteModelAdmin
from product.models import Category,Product,Order,Feedback
# Register your models here.
class ProductAdmin(admin.ModelAdmin,):
    list_display=('name','price','is_available')
    search_fields=('name',)
    list_editable=('is_available',)
    list_filter=('is_available','category')
    
    
    
class OrderAdmin(admin.ModelAdmin):
    list_display=('user','product','quantity','status')
    search_fields=('user','product')
    list_editable=('status',)
    list_filter=('status',)
    
    
        
admin.site.register(Category)
admin.site.register(Feedback)
admin.site.register(Product,ProductAdmin)
admin.site.register(Order,OrderAdmin)


 