"""
Custom middleware for audit logging and organization filtering.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """Log all admin actions for compliance."""
    
    AUDITED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    EXCLUDED_PATHS = ['/api/auth/', '/admin/jsi18n/', '/static/', '/media/']
    
    def process_request(self, request):
        request._audit_enabled = True
        return None
    
    def process_response(self, request, response):
        """Log successful requests that modify data."""
        if not getattr(request, '_audit_enabled', False):
            return response
        
        # Skip if not authenticated
        if not request.user.is_authenticated:
            return response
        
        # Skip excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return response
        
        # Only audit specific methods
        if request.method not in self.AUDITED_METHODS:
            return response
        
        # Only log successful responses
        if not (200 <= response.status_code < 300):
            return response
        
        try:
            # Determine action from method
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            action = action_map.get(request.method, 'unknown')
            
            # Extract model name from path
            path_parts = request.path.strip('/').split('/')
            model_name = path_parts[-2] if len(path_parts) > 1 else path_parts[-1]
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                organization=getattr(request.user, 'organization', None),
                action=action,
                model_name=model_name,
                object_id=path_parts[-1] if len(path_parts) > 0 else 'unknown',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
