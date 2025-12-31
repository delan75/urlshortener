from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import UrlModel
from hashids import Hashids
from .serializers import UrlModelSerializer
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address



class UrlShortenerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_ip = "127.0.0.1"
        self.valid_urls = [
            "https://example.com",
            "http://sub.example.com/path?query=1",
            "http://example.com",
            "http://www.example.com",
            "http://192.168.1.1:8000",
            "http://localhost:8080"
        ]
        self.invalid_urls = [
            "http://",
            "missing..tld", 
            "javascript:alert(1)",
            "http://invalid..com",
            "invalid-.com",
            "invalid.com." 
        ]
        self.hashids = Hashids(salt="urlshortenerapp", min_length=5)

        

    # Model Tests
    
    def test_short_url_generation(self):
        url = UrlModel.objects.create(longUrl="https://example.com")
        encoded_id = self.hashids.encode(url.id)
        self.assertEqual(url.shortUrl, encoded_id)
        self.assertEqual(len(url.shortUrl), 5)

    def test_auto_created_field(self):
        url = UrlModel.objects.create(longUrl="https://example.com")
        self.assertIsNotNone(url.created)

    def test_empty_long_url(self):
        response = self.client.post(
            reverse('create_short_url'),
            {'longUrl': ''},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_short_long_url(self):
        response = self.client.post(
            reverse('create_short_url'),
            {'longUrl': 'c.v'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Serializer Tests
    
    def test_valid_url_formats(self):        
        for url in self.valid_urls:
            serializer = UrlModelSerializer(data={'longUrl': url})
            self.assertTrue(serializer.is_valid(), 
                           f"Failed validation for valid URL: {url}")

    def test_invalid_url_formats(self):        
        for url in self.invalid_urls:
            serializer = UrlModelSerializer(data={'longUrl': url})
            self.assertFalse(serializer.is_valid(), 
                           f"Wrongly validated invalid URL: {url}")

    def test_read_only_fields(self):
        url = UrlModel.objects.create(longUrl="https://example.com")
        data = {
            'longUrl': 'https://new.com',
            'shortUrl': 'modified',
            'visitorIp': '192.168.1.1',
            'completeUrl': 'http://bad.url'
        }
        serializer = UrlModelSerializer(url, data=data)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertNotEqual(updated.shortUrl, 'modified')
        self.assertNotEqual(updated.visitorIp, '192.168.1.1')

    # View Tests

    def test_create_short_url_success(self):
        for url in self.valid_urls:
            response = self.client.post(
                reverse('create_short_url'),
                {'longUrl': url},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auto_http_prefix(self):
        response = self.client.post(
            reverse('create_short_url'),
            {'longUrl': 'www.example.com'},  
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['long_url'], 'http://www.example.com')

    def test_redirect_existing_url(self):
        url = UrlModel.objects.create(longUrl="https://example.com")
        response = self.client.get(
            reverse('redirect_to_long_url', args=[url.shortUrl]),
            follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("https://example.com"))

    def test_redirect_nonexistent_url(self):
        response = self.client.get(reverse('redirect_to_long_url', args=["badcode"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_fetch_all_urls(self):
        UrlModel.objects.create(longUrl="https://example.com")
        response = self.client.get(reverse('fetch_all_urls'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_url(self):
        url = UrlModel.objects.create(longUrl="https://example.com")
        response = self.client.delete(reverse('delete_existing_url', args=[url.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_client_ip_logging(self):
        test_ip = "192.168.1.100"
        response = self.client.post(
            reverse('create_short_url'),
            {'longUrl': 'https://example.com'},
            HTTP_X_FORWARDED_FOR=f"{test_ip}, 10.0.0.1"
        )
        url = UrlModel.objects.first()
        self.assertEqual(url.visitorIp, test_ip)

    # URL Routing Tests

    def test_delete_endpoint_format(self):
        response = self.client.delete('/delete/notanumber/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Edge Cases
    def test_long_url_support(self):
        long_url = "https://example.com/" + "x" * 20000
        response = self.client.post(
            reverse('create_short_url'),
            {'longUrl': long_url},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_special_characters_in_url(self):
        special_url = "https://example.com/üñîçø∂é?query=§¶"
        response = self.client.post(
            reverse('create_short_url'),
            {'longUrl': special_url},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_complete_url_generation(self):
        response = self.client.post(
            reverse('create_short_url'),
            {'longUrl': 'https://example.com'},
            content_type='application/json',
            HTTP_HOST='testserver'
        )
        self.assertIn("http://testserver/", response.data['short_url'])

class RedirectTests(TestCase):
    def test_multiple_redirects(self):
        url = UrlModel.objects.create(longUrl="https://original.com")
        response1 = self.client.get(f'/{url.shortUrl}/')
        response2 = self.client.get(f'/{url.shortUrl}/')
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)

class IpAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_ip = "127.0.0.1"
        self.valid_ips = [
            "192.168.1.1",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8::1",
            "::ffff:192.0.2.128",
            "2001:0db8:0000:0042:0000:8a2e:0370:7334",
        ]
        self.invalid_ips = [
            "192.168.",
            "127.0.0.1.",
            ]
    def test_fetch_urls_based_on_ip(self):
        test_ip = self.test_ip
        UrlModel.objects.create(longUrl="https://example.com", visitorIp=test_ip)
        response = self.client.get(reverse('fetch_user_urls', args=[test_ip]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_valid_ip_address_returned(self):
        response = self.client.get(reverse('test_api'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        
        # validate IP format
        try:
            validate_ipv46_address(response_data['visitorIp'])
        except ValidationError:
            self.fail("Returned IP address is invalid")
    

    


