# ecommerce/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from accounts.views import jwt_auth
from .models import Cart, CartItem, Order, OrderItem, PurchaseRequest, DownloadLog
from notes.models import Note
from papers.models import Paper
import razorpay
from django.urls import reverse

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)




def _user_already_purchased(user, item):
    return (
        OrderItem.objects.filter(
            order__user=user,
            content_type=ContentType.objects.get_for_model(item),
            object_id=item.id,
            order__status='paid'
        ).exists() or
        PurchaseRequest.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(item),
            object_id=item.id,
            status='paid'
        ).exists()
    )

def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@jwt_auth
def add_to_cart(request, item_id):
    item_type = request.GET.get('type', 'note')
    if item_type == 'paper':
        item = get_object_or_404(Paper, id=item_id, is_active=True)
    else:
        item = get_object_or_404(Note, id=item_id, is_active=True)

    if (item.price == 0) and (item.credit_price == 0):
        messages.info(request, "This item is free — open its page to download.")
        return redirect('ecommerce:cart_view')

    if _user_already_purchased(request.user, item):
        messages.info(request, "You already own this item.")
        return redirect(f"{reverse('accounts:profile')}#item-{type}-{item.id}")

    cart = _get_or_create_cart(request.user)
    content_type = ContentType.objects.get_for_model(item)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        content_type=content_type,
        object_id=item.id
    )
    if not created:
        messages.info(request, f"“{item}” is already in your cart.")
    else:
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, f"Added “{item}” to cart.")
    return redirect('ecommerce:cart_view')

@jwt_auth
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    content_type = ContentType.objects.get_for_model(Paper if request.GET.get('type') == 'paper' else Note)
    cart_item = get_object_or_404(CartItem, cart=cart, content_type=content_type, object_id=item_id)
    title = str(cart_item.item)
    cart_item.delete()
    messages.success(request, f"Removed “{title}” from cart.")
    return redirect('ecommerce:cart_view')

@jwt_auth
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related('content_type').all()
    context = {
        'cart': cart,
        'items': items,
        'total_amount': cart.total_amount,
        'total_credits': cart.total_credits,
        'can_pay_with_credits': (
            cart.total_credits > 0 and request.user.credits >= cart.total_credits
        ),
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'ecommerce/cart.html', context)

@jwt_auth
def checkout(request):
    cart = _get_or_create_cart(request.user)
    cart_items = cart.items.select_related('content_type').all()
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('ecommerce:cart_view')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                payment_method=payment_method,
                total_amount=cart.total_amount,
                total_credits=cart.total_credits,
                status='processing' if payment_method == 'razorpay' else 'pending'
            )
            for ci in cart_items:
                OrderItem.objects.create(
                    order=order,
                    content_type=ci.content_type,
                    object_id=ci.object_id,
                    quantity=ci.quantity,
                    price_at_purchase=ci.item.price,
                    credits_at_purchase=ci.item.credit_price,
                )
                PurchaseRequest.objects.get_or_create(
                    user=request.user,
                    content_type=ci.content_type,
                    object_id=ci.object_id,
                    defaults={
                        'order': order,
                        'amount_paid': ci.item.price,
                        'credits_used': ci.item.credit_price,
                        'status': 'pending'
                    }
                )
            if payment_method == 'credits':
                if cart.total_credits <= 0:
                    messages.error(request, "This cart cannot be paid with credits.")
                    return redirect('ecommerce:checkout')
                if request.user.credits < cart.total_credits:
                    messages.error(
                        request,
                        f"Insufficient credits. Needed: {cart.total_credits}, You have: {request.user.credits}"
                    )
                    return redirect('ecommerce:checkout')
                request.user.credits -= cart.total_credits
                request.user.save()
                order.status = 'paid'
                order.paid_at = timezone.now()
                order.save()
                PurchaseRequest.objects.filter(order=order).update(status='paid')
                cart.items.all().delete()
                messages.success(request, "Payment successful! Your downloads are ready.")
                return redirect('accounts:profile')
            elif payment_method == 'razorpay':
                if cart.total_amount <= 0:
                    messages.error(request, "No payable amount found for Razorpay.")
                    return redirect('ecommerce:cart_view')
                try:
                    rp_order = razorpay_client.order.create({
                        'amount': int(cart.total_amount * 100),
                        'currency': 'INR',
                        'receipt': f'order_{order.id}',
                        'payment_capture': 1
                    })
                except Exception as e:
                    messages.error(request, f"Failed to create Razorpay order: {e}")
                    return redirect('ecommerce:cart_view')
                order.razorpay_order_id = rp_order['id']
                order.status = 'processing'
                order.save()
                context = {
                    'cart': cart,
                    'cart_items': cart_items,
                    'order': order,
                    'razorpay_order_id': rp_order['id'],
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'amount_paise': int(cart.total_amount * 100),
                    'user': request.user,
                }
                return render(request, 'ecommerce/checkout.html', context)
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_amount': cart.total_amount,
        'total_credits': cart.total_credits,
        'can_pay_with_credits': (
            cart.total_credits > 0 and request.user.credits >= cart.total_credits
        ),
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'ecommerce/checkout.html', context)

@jwt_auth
@require_POST
@csrf_exempt
def payment_callback(request):
    try:
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({'status': 'error', 'message': 'Missing payment parameters'}, status=400)
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id, user=request.user)
        with transaction.atomic():
            order.razorpay_payment_id = razorpay_payment_id
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()
            PurchaseRequest.objects.filter(order=order).update(status='paid')
            cart = _get_or_create_cart(request.user)
            cart.items.all().delete()
        return JsonResponse({'status': 'success', 'redirect': reverse('accounts:profile')})
    except razorpay.errors.SignatureVerificationError as e:
        return JsonResponse({'status': 'error', 'message': f'Signature verification failed: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@jwt_auth
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    messages.success(request, f"Order #{order.id} completed successfully! Check your purchases in the profile.")
    return redirect('accounts:profile')

@jwt_auth
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'ecommerce/order_history.html', {'orders': orders})

@jwt_auth
def my_purchases(request):
    purchases = PurchaseRequest.objects.filter(user=request.user, status='paid').select_related('content_type').order_by('-created_at')
    return render(request, 'ecommerce/my_purchases.html', {'purchases': purchases})

@jwt_auth
def download_item(request, item_id):
    item_type = request.GET.get('type', 'note')
    if item_type == 'paper':
        item = get_object_or_404(Paper, id=item_id, is_active=True)
    else:
        item = get_object_or_404(Note, id=item_id, is_active=True)
    if _user_already_purchased(request.user, item):
        if not item.pdf_file:
            messages.error(request, f"The file for “{item}” is not available. Please contact support.")
            return redirect('accounts:profile')
        DownloadLog.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(item),
            object_id=item.id,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return redirect(item.pdf_file.url)
    messages.error(request, "You don’t have access to this item.")
    return redirect('ecommerce:cart_view')


from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Cart  # or whatever items you're loading

def marketplace(request):
    items = Cart.objects.all()  # change to your item model
    paginator = Paginator(items, 10)  # 10 items per page

    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'ecommerce/item_list.html', {'items': page_obj})

    return render(request, 'ecommerce/marketplace.html', {'items': page_obj})

