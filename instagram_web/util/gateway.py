import os
from dotenv import load_dotenv
import braintree

gateway = braintree.BraintreeGateway(
	braintree.Configuration(
		environment=os.environ['BT_ENVIRONMENT'],
		merchant_id=os.environ['BT_MERCHANT_ID'],
		public_key=os.environ['BT_PUBLIC_KEY'],
		private_key=os.environ['BT_PRIVATE_KEY']
	)
)