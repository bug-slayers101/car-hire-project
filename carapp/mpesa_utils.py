import requests
import json
import base64
from datetime import datetime
from django.conf import settings

class MpesaAPI:
    @staticmethod
    def get_access_token():
        """Get M-Pesa access token"""
        try:
            consumer_key = settings.MPESA_CONFIG['CONSUMER_KEY']
            consumer_secret = settings.MPESA_CONFIG['CONSUMER_SECRET']

            # Encode credentials
            credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }

            response = requests.get(settings.MPESA_ACCESS_TOKEN_URL, headers=headers)
            response.raise_for_status()

            result = response.json()
            return result['access_token']
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None

    @staticmethod
    def generate_password():
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        business_shortcode = settings.MPESA_CONFIG['BUSINESS_SHORTCODE']
        passkey = settings.MPESA_CONFIG['PASSKEY']

        password_str = f"{business_shortcode}{passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()

        return password, timestamp

    @staticmethod
    def stk_push(phone_number, amount, account_reference, transaction_desc):
        """Initiate STK push"""
        try:
            access_token = MpesaAPI.get_access_token()
            if not access_token:
                return {'error': 'Failed to get access token'}

            password, timestamp = MpesaAPI.generate_password()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'BusinessShortCode': settings.MPESA_CONFIG['BUSINESS_SHORTCODE'],
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': phone_number,
                'PartyB': settings.MPESA_CONFIG['BUSINESS_SHORTCODE'],
                'PhoneNumber': phone_number,
                'CallBackURL': settings.MPESA_CONFIG['CALLBACK_URL'],
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"STK Push request error: {e}")
            return {'error': str(e)}
        except Exception as e:
            print(f"STK Push error: {e}")
            return {'error': str(e)}

    @staticmethod
    def query_stk_status(checkout_request_id):
        """Query STK push status"""
        try:
            access_token = MpesaAPI.get_access_token()
            if not access_token:
                return {'error': 'Failed to get access token'}

            password, timestamp = MpesaAPI.generate_password()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'BusinessShortCode': settings.MPESA_CONFIG['BUSINESS_SHORTCODE'],
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }

            response = requests.post(settings.MPESA_STK_QUERY_URL, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"STK Query error: {e}")
            return {'error': str(e)}