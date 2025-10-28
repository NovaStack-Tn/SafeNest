"""
Email notifications for face detection alerts.
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_unknown_person_alert(detection, organization):
    """
    Send email alert when an unknown person is detected.
    
    Args:
        detection: FaceDetection instance
        organization: Organization instance
    """
    try:
        # Get admin emails from organization
        admin_emails = organization.users.filter(
            is_staff=True
        ).values_list('email', flat=True)
        
        if not admin_emails:
            logger.warning(f"No admin emails found for organization {organization.id}")
            return
        
        # Email subject
        subject = f'⚠️ Security Alert: Unknown Person Detected - {organization.name}'
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                .alert-box {{ background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; }}
                .details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
                .detail-label {{ font-weight: bold; color: #6b7280; }}
                .detail-value {{ color: #111827; }}
                .footer {{ background-color: #374151; color: white; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }}
                .button {{ display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Security Alert</h1>
                    <p style="margin: 5px 0 0 0;">Unknown Person Detected</p>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <h2 style="margin-top: 0; color: #991b1b;">⚠️ Unauthorized Access Attempt</h2>
                        <p><strong>An unknown person has been detected by your surveillance system.</strong></p>
                        <p>This individual is not registered in your face recognition database and requires immediate attention.</p>
                    </div>
                    
                    <div class="details">
                        <h3 style="margin-top: 0; color: #111827;">Detection Details</h3>
                        
                        <div class="detail-row">
                            <span class="detail-label">Organization:</span>
                            <span class="detail-value">{organization.name}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Camera:</span>
                            <span class="detail-value">{detection.camera.name}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Location:</span>
                            <span class="detail-value">{detection.camera.location or 'Not specified'}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Detection Time:</span>
                            <span class="detail-value">{detection.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Confidence Level:</span>
                            <span class="detail-value">{(detection.confidence * 100):.1f}%</span>
                        </div>
                        
                        {f'''<div class="detail-row">
                            <span class="detail-label">Estimated Age:</span>
                            <span class="detail-value">~{detection.age} years</span>
                        </div>''' if detection.age else ''}
                        
                        {f'''<div class="detail-row">
                            <span class="detail-label">Gender:</span>
                            <span class="detail-value">{'Male' if detection.gender == 'M' else 'Female'}</span>
                        </div>''' if detection.gender else ''}
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:3000/camera-history" class="button">
                            View Full Details in Dashboard
                        </a>
                    </div>
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                        <h4 style="margin-top: 0; color: #92400e;">⚡ Recommended Actions:</h4>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Review the detection in your dashboard immediately</li>
                            <li>Check camera footage for additional context</li>
                            <li>Verify if this person should have access</li>
                            <li>Consider enrolling them if they are authorized</li>
                            <li>Alert security personnel if necessary</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p style="margin: 0;">SafeNest Security System</p>
                    <p style="margin: 5px 0 0 0;">This is an automated security alert. Do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
SECURITY ALERT: Unknown Person Detected

Organization: {organization.name}
Camera: {detection.camera.name}
Location: {detection.camera.location or 'Not specified'}
Time: {detection.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Confidence: {(detection.confidence * 100):.1f}%
{f'Age: ~{detection.age} years' if detection.age else ''}
{f"Gender: {'Male' if detection.gender == 'M' else 'Female'}" if detection.gender else ''}

An unknown person has been detected by your surveillance system.
This individual is not registered in your face recognition database.

Please review the detection in your dashboard immediately:
http://localhost:3000/camera-history

SafeNest Security System
        """
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(admin_emails)
        )
        email.attach_alternative(html_content, "text/html")
        
        # Attach face image if available
        if detection.frame_image:
            try:
                email.attach_file(detection.frame_image.path)
            except Exception as e:
                logger.error(f"Failed to attach image: {e}")
        
        # Send email
        email.send(fail_silently=False)
        logger.info(f"Unknown person alert sent to {len(admin_emails)} admin(s) for org {organization.id}")
        
    except Exception as e:
        logger.error(f"Failed to send unknown person alert: {e}", exc_info=True)


def send_daily_security_summary(organization, stats):
    """
    Send daily summary of security detections.
    
    Args:
        organization: Organization instance
        stats: Dictionary with detection statistics
    """
    try:
        admin_emails = organization.users.filter(
            is_staff=True
        ).values_list('email', flat=True)
        
        if not admin_emails:
            return
        
        subject = f'📊 Daily Security Summary - {organization.name}'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .stats {{ display: flex; justify-content: space-around; padding: 20px; }}
                .stat {{ text-align: center; }}
                .stat-value {{ font-size: 36px; font-weight: bold; }}
                .stat-label {{ color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Daily Security Summary</h1>
                    <p>{organization.name}</p>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{stats.get('total', 0)}</div>
                        <div class="stat-label">Total Detections</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #10b981;">{stats.get('matched', 0)}</div>
                        <div class="stat-label">Authorized</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #ef4444;">{stats.get('unknown', 0)}</div>
                        <div class="stat-label">Unknown</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Daily Security Summary\nTotal: {stats.get('total', 0)}\nAuthorized: {stats.get('matched', 0)}\nUnknown: {stats.get('unknown', 0)}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(admin_emails)
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Daily summary sent to {len(admin_emails)} admin(s) for org {organization.id}")
        
    except Exception as e:
        logger.error(f"Failed to send daily summary: {e}", exc_info=True)
