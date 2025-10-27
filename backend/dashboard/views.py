"""
Dashboard API views - aggregate statistics and KPIs.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


class DashboardStatsView(APIView):
    """Main dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.organization:
            return Response({'error': 'User has no organization'}, status=400)
        
        org = user.organization
        time_range = request.query_params.get('range', '7d')
        
        # Parse time range
        time_map = {'24h': 1, '7d': 7, '30d': 30}
        days = time_map.get(time_range, 7)
        since = timezone.now() - timedelta(days=days)
        
        from security.models import LoginEvent, Alert
        from incidents.models import Incident
        from faces.models import FaceDetection
        
        stats = {
            'time_range': time_range,
            'logins': {
                'total': LoginEvent.objects.filter(user__organization=org, timestamp__gte=since).count(),
                'successful': LoginEvent.objects.filter(user__organization=org, timestamp__gte=since, success=True).count(),
                'failed': LoginEvent.objects.filter(user__organization=org, timestamp__gte=since, success=False).count(),
                'anomalies': LoginEvent.objects.filter(user__organization=org, timestamp__gte=since, is_anomaly=True).count(),
            },
            'alerts': {
                'total': Alert.objects.filter(organization=org, created_at__gte=since).count(),
                'open': Alert.objects.filter(organization=org, status='open').count(),
                'critical': Alert.objects.filter(organization=org, severity='critical', created_at__gte=since).count(),
            },
            'incidents': {
                'total': Incident.objects.filter(organization=org, opened_at__gte=since).count(),
                'open': Incident.objects.filter(organization=org, status='open').count(),
                'critical': Incident.objects.filter(organization=org, severity='critical', opened_at__gte=since).count(),
            },
            'faces': {
                'detections': FaceDetection.objects.filter(camera__organization=org, timestamp__gte=since).count(),
                'matches': FaceDetection.objects.filter(camera__organization=org, timestamp__gte=since, is_match=True).count(),
            }
        }
        
        return Response(stats)


class RecentActivityView(APIView):
    """Recent security activity feed."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.organization:
            return Response({'error': 'User has no organization'}, status=400)
        
        org = user.organization
        limit = int(request.query_params.get('limit', 20))
        
        from security.models import Alert
        from incidents.models import Incident
        
        alerts = Alert.objects.filter(organization=org).order_by('-created_at')[:limit]
        incidents = Incident.objects.filter(organization=org).order_by('-opened_at')[:limit//2]
        
        activity = []
        
        for alert in alerts:
            activity.append({
                'type': 'alert',
                'id': alert.id,
                'title': alert.title,
                'severity': alert.severity,
                'timestamp': alert.created_at.isoformat()
            })
        
        for incident in incidents:
            activity.append({
                'type': 'incident',
                'id': incident.id,
                'title': incident.title,
                'severity': incident.severity,
                'timestamp': incident.opened_at.isoformat()
            })
        
        # Sort by timestamp
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({'activity': activity[:limit]})


class RiskMapView(APIView):
    """Geographic risk map data."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.organization:
            return Response({'error': 'User has no organization'}, status=400)
        
        from security.models import LoginEvent
        
        org = user.organization
        since = timezone.now() - timedelta(days=30)
        
        # Get login events by country
        events = LoginEvent.objects.filter(
            user__organization=org,
            timestamp__gte=since
        ).values('country_code', 'country_name').annotate(
            total=Count('id'),
            anomalies=Count('id', filter=Q(is_anomaly=True))
        ).order_by('-total')[:20]
        
        return Response({'countries': list(events)})
