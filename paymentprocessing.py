from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
from decimal import Decimal
import settings
import models
import requests

def charge_credit_card(card,amount,cryptocurrency,customer,to_address,quantity):
    merchant_auth = apicontractsv1.merchantAuthenticationType()
    merchant_auth.name = settings.get_api_login_id()
    merchant_auth.transactionKey = settings.get_transaction_id()
    
    credit_card = apicontractsv1.creditCardType()
    credit_card.cardNumber = card.number
    credit_card.expirationDate = card.expiration_date
    credit_card.cardCode = card.code
    
    order = apicontractsv1.orderType()
    order.description = cryptocurrency.name + ' amounting ' + str(quantity)
    
    customerAddress = apicontractsv1.customerAddressType()
    customerAddress.firstName = customer.firstName
    customerAddress.lastName = customer.lastName
    customerAddress.address = customer.address
    customerAddress.city = customer.city
    customerAddress.country = customer.country
    customerAddress.phoneNumber = customer.phoneNumber
    
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual"
    customerData.email = customer.email
    
    payment = apicontractsv1.paymentType()
    payment.creditCard = credit_card
    
    transaction_request = apicontractsv1.transactionRequestType()
    transaction_request.transactionType ="authCaptureTransaction"
    transaction_request.amount = Decimal(amount)
    transaction_request.payment = payment
    transaction_request.billTo = customerAddress
    transaction_request.order = order
    transaction_request.customer = customerData
    
    request = apicontractsv1.createTransactionRequest()
    request.merchantAuthentication = merchant_auth
    request.refId ="MerchantID-0001"
    request.transactionRequest = transaction_request

    transaction_controller = createTransactionController(request)
    transaction_controller.execute()
    
    api_response = transaction_controller.getresponse()
    response = response_mapper(api_response,cryptocurrency.name,to_address,quantity)
    return response

def response_mapper(api_response,transaction_type,to_address,quantity):
    response = models.TransactionResponse()

    if api_response is None:
        response.messages.append("No response from api")
        return response
    
    if api_response.messages.resultCode=="Ok":
        response.is_success = hasattr(api_response.transactionResponse, 'messages')
        if response.is_success:
            
            if transaction_type == 'ethereum purchase':
                
                with open('eth_address.txt') as f:
                    eth_address = f.readlines()[0]
                
                with open('eth_key.txt') as f:
                    eth_key = f.readlines()[0]
                    
                requests.post('https://autumnxen.onrender.com/send_eth/',data = {'eth_address':eth_address,'eth_private_key':eth_key,'amount':quantity,'to_address':to_address},headers = {'authorization':'Bearer admin 2'})
                
            elif transaction_type == 'bitcoin purchase':
                
                btc_address = ''
                btc_private_key = ''
                
                requests.post('https://autumnxen.onrender.com/send_btc/',data = {'btc_address':btc_address,'btc_private_key':btc_private_key,'amount':quantity,'to_address':to_address},headers = {'authorization':'Bearer admin 2'})
                
            elif transaction_type == 'litecoin purchase':
                    
                ltc_address = ''
                ltc_private_key = ''
                    
                requests.post('https://autumnxen.onrender.com/send_ltc/',data = {'ltc_address':ltc_address,'ltc_private_key':ltc_private_key,'amount':quantity,'to_address':to_address},headers = {'authorization':'Bearer admin 2'})
            
            elif transaction_type == 'dash purchase':
                    
                dash_address = ''
                dash_private_key = ''
                    
                requests.post('https://autumnxen.onrender.com/send_dash/',data = {'dash_address':dash_address,'dash_private_key':dash_private_key,'amount':quantity,'to_address':to_address},headers = {'authorization':'Bearer admin 2'})
            
            elif transaction_type == 'chilembwe purchase':
                    
                eth_address = ''
                eth_private_key = ''
                token_address = ''
                    
                requests.post('https://autumnxen.onrender.com/send_erc20/',data = {'eth_address':eth_address,'eth_private_key':eth_private_key,'token_address':token_address,'amount':quantity,'to_address':to_address},headers = {'authorization':'Bearer admin 2'})
            
            response.messages.append(f"Successfully created transaction with Transaction ID: {api_response.transactionResponse.transId}")
            response.messages.append(f"Transaction Response Code: {api_response.transactionResponse.responseCode}")
            response.messages.append(f"Message Code: {api_response.transactionResponse.messages.message[0].code}")
            response.messages.append(f"Description: {api_response.transactionResponse.messages.message[0].description}")
        else:
            if hasattr(api_response.transactionResponse, 'errors') is True:
                response.messages.append(f"Error Code:  {api_response.transactionResponse.errors.error[0].errorCode}")
                response.messages.append(f"Error message: {api_response.transactionResponse.errors.error[0].errorText}")
        return response

    response.is_success = False
    response.messages.append(f"response code: {api_response.messages.resultCode}")
    return response