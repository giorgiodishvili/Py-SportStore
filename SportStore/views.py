from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, CheckoutForm, BulkUploadForm
from .models import Product, Cart, CartItem, Order, OrderItem, Wishlist, WishlistItem, Review
import pandas as pd
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import UserProfileForm
from .forms import ReviewForm


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'SportStore/profile.html', {'form': form})


def landing(request):
    category = request.GET.get('category')
    products = Product.objects.all()
    if category:
        products = products.filter(category=category)
    return render(request, 'SportStore/landing.html', {'products': products, 'category': category})


def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'SportStore/search_results.html', {'products': products, 'query': query})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        messages.error(request, 'Sorry, this product is out of stock.')
        return redirect('product_detail', product_id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, 'Sorry, not enough stock available.')
    else:
        cart_item.quantity = 1
        cart_item.save()
    return redirect('view_cart')


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                total_price=total,
            )
            for item in cart_items:
                if item.quantity > item.product.stock:
                    messages.error(request, f'Not enough stock for {item.product.name}.')
                    return redirect('view_cart')
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()
            cart.items.all().delete()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'SportStore/checkout.html', {'form': form, 'total': total})



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Your review has been submitted successfully.')
            return redirect('product_detail', product_id=product_id)
    else:
        review_form = ReviewForm()
    return render(request, 'SportStore/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing')
    else:
        form = AuthenticationForm()
    return render(request, 'SportStore/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'SportStore/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'SportStore/cart.html', {'cart': cart, 'total': total})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'SportStore/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'SportStore/my_orders.html', {'orders': orders})


@staff_member_required
def bulk_upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                Product.objects.create(
                    name=row['name'],
                    description=row['description'],
                    price=row['price'],
                    image_url=row['image_url'],
                    category=row['category'],
                    stock=row['stock']  # Assuming you've added a stock field in the Product model
                )
            messages.success(request, 'Products uploaded successfully!')
            return redirect('bulk_upload')
    else:
        form = BulkUploadForm()
    return render(request, 'SportStore/bulk_upload.html', {'form': form})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    if created:
        messages.success(request, 'Product added to wishlist')
    else:
        messages.info(request, 'Product is already in your wishlist')
    return redirect('wishlist')


@login_required
def view_wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'SportStore/wishlist.html', {'wishlist': wishlist})
