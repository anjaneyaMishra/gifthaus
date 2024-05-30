from django.shortcuts import render
from django.db.models import Q
from product.models import Product

# Create your views here.
def index(request):
   #return HttpResponse("<h1>Hello World</h1>")
   return render(request,'pages/index.html')

def aboutus(request):
    #return HttpResponse("<h2>About Us</h2>")
    #name="John"
    
    return render(request,'pages/about.html')
 
 
 


def search(request):
   query = request.GET.get('q')
   products = []

   if query:
        # Use Q objects to perform a case-insensitive search on title and description
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(image__icontains=query)
        )

   context = {
        'query': query,
        'products': products,
    }
   return render(request, 'pages/results.html',context) 
