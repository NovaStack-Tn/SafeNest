"""
Utility functions for security app.
"""
import re
import hashlib
from user_agents import parse


def parse_user_agent(user_agent_string):
    """Parse user agent string and extract device info."""
    if not user_agent_string:
        return {}
    
    user_agent = parse(user_agent_string)
    
    return {
        'device_type': 'mobile' if user_agent.is_mobile else ('tablet' if user_agent.is_tablet else 'desktop'),
        'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
        'os': f"{user_agent.os.family} {user_agent.os.version_string}",
    }


def get_ip_geolocation(ip_address):
    """Get geolocation data for IP address."""
    # In production, use a service like MaxMind GeoIP2, ipapi, or ip-api
    # For now, return empty dict
    # TODO: Integrate with geolocation service
    return {
        'country_code': '',
        'country_name': '',
        'city': '',
        'latitude': None,
        'longitude': None,
    }


def calculate_device_fingerprint(user_agent, ip_address):
    """Create a simple device fingerprint."""
    fingerprint_string = f"{user_agent}|{ip_address}"
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:32]


def calculate_travel_velocity(event1, event2):
    """Calculate travel velocity between two login events."""
    from math import radians, cos, sin, asin, sqrt
    
    # Haversine formula to calculate distance
    if not all([event1.latitude, event1.longitude, event2.latitude, event2.longitude]):
        return None
    
    lon1, lat1, lon2, lat2 = map(
        radians,
        [event1.longitude, event1.latitude, event2.longitude, event2.latitude]
    )
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # Radius of earth in kilometers
    
    # Calculate time difference in hours
    time_diff = (event2.timestamp - event1.timestamp).total_seconds() / 3600
    
    if time_diff == 0:
        return float('inf')
    
    # Return velocity in km/h
    return km / time_diff
