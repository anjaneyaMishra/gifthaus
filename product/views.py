from django.shortcuts import render
from django.core.paginator import Paginator

# Create your views here.
from django.shortcuts import render,get_object_or_404,redirect
from django.core.mail import send_mail
from django.conf import settings
from product.models import Product,Category,Order,Feedback
from user.models import Address
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import date,timedelta
# Create your views here.
def all_products(request):
    products=Product.objects.all()
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
     
    categories=Category.objects.all().order_by('category')
   
    print(products.query)
    context= {
        # "products" : products,
        "page_obj": page_obj,
        "categories" : categories
    }
    return render(request,"product/products.html", context)



def product_details(request,id):
    product=get_object_or_404(Product, id=id)
    quantity=1
    if request.session.get('cart_items'):
        if request.session.get('cart_items').get(str(id)):
            quantity = request.session.get('cart_items')[str(id)]
    context={
        "product" : product,
        "quantity":quantity,
        
    }
    return render(request,"product/product.html",context)

def category_products(request,cid):
    products=Product.objects.filter(category=cid)
    categories=Category.objects.all().order_by('category')
    print(products.query)
    context= {
        "products" : products,
        "categories" : categories
    }
    return render(request,"product/products.html", context)


def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity=request.POST.get("quantity")
        cart_items={}
        if request.session.get("cart_items"):
            cart_items=request.session.get("cart_items")
        cart_items[product_id]=quantity
        request.session["cart_items"]=cart_items
        print(request.session.get("cart_items"))
    return redirect("cart")


def cart(request):
    cart_details, total_price=get_cart_details(request)
    context={
        "products":cart_details,
        "total_price":total_price,
    }
    return render(request,'product/cart.html',context)


def remove_from_cart(request, id):
     cart_items = request.session.get('cart_items')
     del cart_items[str(id)]
     request.session['cart_items'] = cart_items
     return redirect("cart")
 

def check_out(request):
    addresses=Address.objects.filter(user=request.user)
    cart_details,total_price = get_cart_details(request)
    context={
        "addresses":addresses,
        "products":cart_details,
        "total_price":total_price
    }
    return render(request,'product/check_out.html',context)


def place_order(request):
    if request.method== "POST":
        user=request.user
        address=request.POST.get("address")
        address=Address.objects.get(id=address)
        payment_mode=request.POST.get("payment_mode")
        cart_details,total_price=get_cart_details(request)
        orders =[]
        for product in cart_details:
            order=Order(
                product=Product.objects.get(id=product['id']),
                user=user,
                address=address,
                quantity= product['quantity'],
                price=product['price'],
                payment_method=payment_mode
            )
            orders.append(order)
        Order.objects.bulk_create(orders)
        mail_context= {
            "username" : request.user.first_name+" "+request.user.last_name,
            "books" : cart_details,
            "delivery_date": date.today()+ timedelta(days=7),
            "total_price" : total_price
        }
        
        subject = "Order is Placed successfully"
        # body= f"Your Order is Placed successfully. Amount {total_price}. Deliver Address : {address}"
        html_message = render_to_string('product/mail_template.html',mail_context)
        plain_message=strip_tags(html_message)
        to = [request.user.email]
        from_email=settings.EMAIL_HOST_USER
    
        # send_mail(subject=subject,message=body,from_email=from_email,recipient_list=to,fail_silently=False)
        send_mail(subject=subject,message=plain_message,from_email=from_email,recipient_list=to,fail_silently=False,html_message=html_message)
        
        
        request.session['cart_items']={}
        return redirect('orders')    


def orders(request):
    orders=Order.objects.filter(user=request.user).order_by('-id')
    context={
        "orders" : orders
    }    
    return render(request,'product/orders.html',context)


def add_feedback(request):
    if request.method == "POST":
        user=request.user
        product_id=request.POST.get("product_id")
        product=Product.objects.get(id=product_id)
        rating=request.POST.get("rating")
        comment=request.POST.get("comment")
        feedback=None
        try:
            feedback=Feedback.objects.get(user=user,product=product)
        except:
            print("Feedback Not Available")
            
    if feedback is None:
        feedback=Feedback()
        feedback.user=user
        feedback.product=product
    feedback.rating=rating
    feedback.comment=comment
    feedback.save()
    return redirect('orders')




def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'Placed':
        order.status = 'Cancelled'
        order.save()
    
    return redirect('orders')




def get_cart_details(request):
    total_price=0
    cart_details=[]
    if not request.session.get('cart_items'):
        return cart_details,total_price
    cart_items = request.session.get('cart_items')
    products=Product.objects.filter(id__in=list(cart_items.keys()))
    for product in products:
        quantity_str = cart_items.get(str(product.id), '0')  
        if quantity_str.isdigit():  
            quantity = int(quantity_str)
            price=quantity * product.price
            total_price += price
            cart_details.append({
                "id":product.id,
                "name":product.name,
                "quantity":quantity,
                "price":price,
                "image":product.image
            })
    return cart_details,total_price
