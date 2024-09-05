import yookassa
import uuid
import os

from yookassa import Payment
from dotenv import load_dotenv

load_dotenv()
yookassa.Configuration.account_id = os.getenv('ACCOUNT_ID')
yookassa.Configuration.secret_key = os.getenv('SECRET_KEY')

def create(amount, chat_id):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            'value': amount,
            'currency': "RUB"
        },
        'payment_method_data': {
            'type': 'bank_card'
        },
        'confirmation': {
            'type' : 'redirect',
            'return_url': 'https://t.me/sale_71_bot'
        },
        'capture': True,
        'metadate': {
            'chat_id': chat_id
        },
        'description': {
            'Описание товара...'
        }
    }, id_key)
    
    return payment.confirmation.confirmation_url, payment.id