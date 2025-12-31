from rest_framework import serializers
from .models import UrlModel
import re

class UrlModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlModel
        fields = ['id','longUrl', 'shortUrl', 'visitorIp', 'completeUrl', 'created']
        read_only_fields = ['shortUrl', 'visitorIp', 'completeUrl', 'created'] 

    def validate_longUrl(self, value):
        pattern = re.compile(
            r'^'
            r'(?:'
            r'([a-zA-Z][a-zA-Z0-9+.-]*://)'
            r'(?:[^/:@]+(?::[^/:@]*)?@)?'     
            r'(?:'
            r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'  # Domain
            r'|localhost'                      
            r'|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
            r'|\[[a-fA-F0-9:]+\]'             
            r')'
            r'|'
            r'(?![^/]*@)'                      
            r'(?:'
            r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'  
            r'|localhost'                     
            r'|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'  
            r'|\[[a-fA-F0-9:]+\]'             
            r')'
            r')'
            r'(?::\d+)?'                       
            r'(?:[/?#][^\s]*)?'                
            r'$',
        re.IGNORECASE
        )
        if not pattern.match(value):
            raise serializers.ValidationError(
                "Enter a valid URL (e.g., http://example.com, https://example.com, or example.com)"
            )
        return value
    
class VisitorIpSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlModel
        fields = ['longUrl', 'shortUrl', 'completeUrl', 'created']
        read_only_fields = ['shortUrl', 'completeUrl', 'created']