from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UrlModel
from django.shortcuts import redirect
from .serializers import UrlModelSerializer, VisitorIpSerializer
from django.http import JsonResponse

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Create your views here.
@api_view(['POST'])
def createShortUrl(request):
    ip = get_client_ip(request)
    longUrl = request.data.get('longUrl')
    serializer = UrlModelSerializer(data=request.data)
    if serializer.is_valid():
        if longUrl == 'c.v':
            return Response({'message': 'Too short'}, status=400)
        if not longUrl.startswith(('http://', 'https://')):
            longUrl = 'http://' + longUrl
        urlModel = serializer.save()  
        urlModel.visitorIp = ip
        urlModel.longUrl = longUrl  

        # Generate full URL for shortURL
        base_url = request.build_absolute_uri('/')  
        urlModel.completeUrl = f"{base_url}{urlModel.shortUrl}/"
        
        urlModel.save()  
        return Response({
            "message": f"Short URL with ID: {urlModel.id}, created successfully",
            "short_code": urlModel.shortUrl,
            "short_url": urlModel.completeUrl,
            "long_url": urlModel.longUrl
        }, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'POST'])
def redirectToLongUrl(request, shortUrl):
    try:
        urlModel = UrlModel.objects.get(shortUrl=shortUrl)
        longUrl = urlModel.longUrl
        urlModel.save()

        return redirect(longUrl)
    except UrlModel.DoesNotExist:
        return Response({'message': 'Short URL not found'}, status=404)
    

#fetch all stored urls
@api_view(['GET'])
def fetchAllUrls(request):
    urls = UrlModel.objects.all()
    serializer = UrlModelSerializer(urls, many=True)
    return Response(serializer.data)

#delete url based on id
@api_view(['DELETE'])
def deleteExistingUrl(request, id):
    try:
        urlModel = UrlModel.objects.get(id=id)
        urlModel.delete()
        return Response({'message': 'URL deleted successfully'}, status=204)
    except UrlModel.DoesNotExist:
        return Response({'message': 'URL not found'}, status=404)
    
#fetch store urls based on a particular ip address
@api_view(['GET'])
def fetchUserUrls(request, visitorIp):
    urls = UrlModel.objects.filter(visitorIp=visitorIp)
    serializer = VisitorIpSerializer(urls, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def testAPI(request):
    visitor_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    return JsonResponse({'visitorIp': visitor_ip})

@api_view(['GET'])
def fetch_user_urls(request, visitorIp):
    urls = UrlModel.objects.filter(visitorIp=visitorIp)
    serializer = UrlModelSerializer(urls, many=True)
    return Response(serializer.data)