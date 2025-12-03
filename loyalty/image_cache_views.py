"""
View ها و API برای مدیریت کش تصاویر
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import ImageCache, Product, Slider
from .image_cache import ImageCacheManager


@login_required
@require_http_methods(["GET"])
def cache_status_view(request):
    """
    نمایش وضعیت کش تصاویر
    """
    try:
        # آمار کلی
        total_cache = ImageCache.objects.count()
        cache_with_data = ImageCache.objects.filter(
            Q(image_data__isnull=False) | Q(image_url__isnull=False)
        ).count()
        
        # آمار بر اساس نوع مدل
        products_cache = ImageCache.objects.filter(content_type='loyalty.product').count()
        sliders_cache = ImageCache.objects.filter(content_type='loyalty.slider').count()
        
        # تصاویر بدون کش
        products_without_cache = Product.objects.filter(
            image__isnull=False
        ).exclude(image='').count() - products_cache
        
        sliders_without_cache = Slider.objects.filter(
            image__isnull=False
        ).exclude(image='').count() - sliders_cache
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'total_cached': total_cache,
                'cache_with_data': cache_with_data,
                'products': {
                    'cached': products_cache,
                    'without_cache': max(0, products_without_cache)
                },
                'sliders': {
                    'cached': sliders_cache,
                    'without_cache': max(0, sliders_without_cache)
                }
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def cache_all_images_view(request):
    """
    کش کردن همه تصاویر موجود
    """
    try:
        result = ImageCacheManager.cache_all_images()
        return JsonResponse({
            'status': 'success',
            'message': f'{result["cached"]} تصویر کش شد',
            'data': result
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_cache_status(request):
    """
    API endpoint برای دریافت وضعیت کش
    """
    try:
        total_cache = ImageCache.objects.count()
        cache_with_data = ImageCache.objects.filter(
            Q(image_data__isnull=False) | Q(image_url__isnull=False)
        ).count()
        
        products_cache = ImageCache.objects.filter(content_type='loyalty.product').count()
        sliders_cache = ImageCache.objects.filter(content_type='loyalty.slider').count()
        
        return Response({
            'total_cached': total_cache,
            'cache_with_data': cache_with_data,
            'products_cached': products_cache,
            'sliders_cached': sliders_cache
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_cache_all(request):
    """
    API endpoint برای کش کردن همه تصاویر
    """
    try:
        result = ImageCacheManager.cache_all_images()
        return Response({
            'message': f'{result["cached"]} images cached',
            'cached': result['cached'],
            'errors': result['errors'],
            'total': result['total']
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

