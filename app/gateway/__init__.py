import os
import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=braintree.Environment.Sandbox,
        merchant_id='vw3v93q6kvbc3hkr',
        public_key='9sjrn4r44hdq7jsj',
        private_key='0d52b60d63751972d2b304dc0bc3ed12'
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)
