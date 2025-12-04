"""
Twilio utility functions for sending and verifying OTP codes via SMS
"""
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


def get_twilio_client():
    """Get Twilio client instance"""
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    
    if not account_sid or not auth_token:
        raise ValueError("Twilio credentials not configured")
    
    return Client(account_sid, auth_token)


def send_otp(phone):
    """
    Send OTP code to phone number using Twilio Verify service
    Supports European phone numbers
    
    Args:
        phone (str): Phone number in E.164 format (e.g., +1234567890, +491234567890)
    
    Returns:
        dict: {
            'success': bool,
            'status': str,
            'message': str
        }
    """
    try:
        verify_sid = settings.TWILIO_VERIFY_SERVICE_SID
        
        if not verify_sid:
            # Fallback: Use Messaging API if Verify service is not configured
            return {
                'success': False,
                'status': 'error',
                'message': 'Twilio Verify Service SID not configured. Please set TWILIO_VERIFY_SERVICE_SID in settings.'
            }
        
        client = get_twilio_client()
        
        # Format phone number to E.164 format if needed
        phone = format_phone_number(phone)
        
        verification = client.verify.services(verify_sid).verifications.create(
            to=phone,
            channel='sms'
        )
        
        return {
            'success': True,
            'status': verification.status,
            'message': 'OTP code sent successfully'
        }
    
    except TwilioRestException as e:
        return {
            'success': False,
            'status': 'error',
            'message': f'Twilio error: {e.msg}',
            'error_code': e.code
        }
    except Exception as e:
        return {
            'success': False,
            'status': 'error',
            'message': f'Error sending OTP: {str(e)}'
        }


def check_otp(phone, code):
    """
    Verify OTP code entered by user
    
    Args:
        phone (str): Phone number in E.164 format
        code (str): OTP code entered by user
    
    Returns:
        dict: {
            'success': bool,
            'status': str,
            'approved': bool,
            'message': str
        }
    """
    try:
        verify_sid = settings.TWILIO_VERIFY_SERVICE_SID
        
        if not verify_sid:
            return {
                'success': False,
                'status': 'error',
                'approved': False,
                'message': 'Twilio Verify Service SID not configured'
            }
        
        client = get_twilio_client()
        
        # Format phone number to E.164 format if needed
        phone = format_phone_number(phone)
        
        verification_check = client.verify.services(verify_sid).verification_checks.create(
            to=phone,
            code=code
        )
        
        approved = verification_check.status == 'approved'
        
        return {
            'success': True,
            'status': verification_check.status,
            'approved': approved,
            'message': 'OTP verified successfully' if approved else 'Invalid OTP code'
        }
    
    except TwilioRestException as e:
        # Handle specific Twilio errors
        if e.code == 20404:
            return {
                'success': False,
                'status': 'error',
                'approved': False,
                'message': 'Verification not found. Please request a new code.'
            }
        elif e.code == 20403:
            return {
                'success': False,
                'status': 'error',
                'approved': False,
                'message': 'Invalid verification code'
            }
        else:
            return {
                'success': False,
                'status': 'error',
                'approved': False,
                'message': f'Twilio error: {e.msg}',
                'error_code': e.code
            }
    except Exception as e:
        return {
            'success': False,
            'status': 'error',
            'approved': False,
            'message': f'Error verifying OTP: {str(e)}'
        }


def format_phone_number(phone):
    """
    Format phone number to E.164 format (required by Twilio)
    Supports European phone numbers
    
    Args:
        phone (str): Phone number in various formats
    
    Returns:
        str: Phone number in E.164 format (e.g., +491234567890)
    """
    # Remove all non-digit characters except +
    phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # If phone doesn't start with +, add country code
    if not phone.startswith('+'):
        # Try to detect country code
        # For European numbers, common patterns:
        # - Germany: +49
        # - France: +33
        # - UK: +44
        # - Italy: +39
        # - Spain: +34
        # etc.
        
        # If starts with 0, remove it (common in European formats)
        if phone.startswith('0'):
            phone = phone[1:]
        
        # Default to +49 (Germany) if no country code detected
        # You can modify this logic based on your needs
        # For now, we'll assume the phone already has country code or add +49
        if len(phone) >= 10:
            # Likely has country code already
            phone = '+' + phone
        else:
            # Assume German number
            phone = '+49' + phone
    
    return phone

