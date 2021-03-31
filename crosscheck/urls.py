from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from crosscheckapi.views import register_user, login_user
from crosscheckapi.views import Tenants, Payments, Properties, PaymentTypes

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tenants', Tenants, 'tenant')
router.register(r'payments', Payments, 'payment')
router.register(r'properties', Properties, 'property')
router.register(r'paymenttypes', PaymentTypes, 'paymenttype')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
]
