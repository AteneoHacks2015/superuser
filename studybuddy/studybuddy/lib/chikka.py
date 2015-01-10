import requests

CLIENT_ID = '1083ae71885cb6c0c739b46d6e462c2cdbd2d8a3b16f637ccea7dfa755f3b09e'
SECRET_KEY = 'f62bd452f23fdc0bee8bbf1a53102661b7b9accb7f48c835f4644cfd052870c7'
SHORT_CODE = '292901232'

#receive
def send_sms(number="", message="", message_id=""): 
    data = {
        'message_type':'SEND',
        'client_id':CLIENT_ID,
        'secret_key':SECRET_KEY,
        'shortcode':SHORT_CODE,
        'mobile_number':number,
        'message':message,
        'message_id':message_id
    }

    r = requests.post('https://post.chikka.com/smsapi/request', data)
    return r
