from django.urls import path
from .views import (
    createShortUrl, 
    redirectToLongUrl, 
    testAPI, 
    fetchAllUrls, 
    deleteExistingUrl,
    fetchUserUrls
)


urlpatterns = [
    #test API
    path('test/', testAPI, name='test_api'),

    path('create/', createShortUrl, name='create_short_url'),
    path('all/', fetchAllUrls, name='fetch_all_urls'),
    path('myUrls/<str:visitorIp>/', fetchUserUrls, name='fetch_user_urls'),
    path('fetch_user_urls/<str:visitorIp>/', fetchUserUrls, name='fetch_user_urls'),
    path('<str:shortUrl>/', redirectToLongUrl, name='redirect_to_long_url'),
    path('delete/<int:id>/', deleteExistingUrl, name='delete_existing_url'),

]