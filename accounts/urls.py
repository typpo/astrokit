from django.conf.urls import url
from .views import (
    LoginView,
    LogoutView,
    RegistrationView,
    MyImageList,
    BrowseImageList,
    ForgotPasswordView,
    ResetPasswordView,
    )

urlpatterns = (
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    url(r'^reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    url(r'^register/', RegistrationView.as_view(), name='register'),
    url(r'^my-image-list/', MyImageList.as_view(), name='my-image-list'),
    url(r'^browse-images/', BrowseImageList.as_view(), name='browse-image-list'),
)
