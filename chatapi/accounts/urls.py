from django.urls import path
import accounts.views as views

user_viewset = views.UserViewSet.as_view({
    'post': 'generate_otp'
})

urlpatterns = [
    path('generate-otp/', user_viewset, name='generate_otp'),
    path('verify-otp/', views.UserViewSet.as_view({'post': 'verify_otp'}), name='verify_otp'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]


