from deta import Deta

from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status,Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

import uvicorn

app = FastAPI()

#### Home route

@app.get('/',tags = ['Home'])
async def home():
    return 'C-crypto Wallet'

##########################################################################################
######## Authorisation and initialising database
#########################################################################################

with open('deta.txt') as f:
    deta_base_key = f.readlines()
    
with open('admin.txt') as f:
    admin1 = f.readlines()
       
deta = Deta(deta_base_key[0])

admin = deta.Base('admin_details')

admin_db = {
    admin1[0]: admin.fetch()._items[0]
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def decode_token(token):
    user = get_user(admin_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token",tags = ['Log In'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = admin_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    password_ = form_data.password
    if not password_ == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


###############################################################################
############## Buying crypto
###############################################################################


import models
import paymentprocessing

from pycoingecko import CoinGeckoAPI

coinGecko = CoinGeckoAPI()

def amount(crypto_name,quantity):
    
    prices = coinGecko.get_price(ids=['bitcoin','ethereum'], vs_currencies='usd')
    
    price = prices[crypto_name]['usd']

    return str(price * quantity)
    

@app.post('/buy_crypto/',tags = ['Buy Cryptocurrency'])
async def buy_crypto(firstname : str = Form(...),lastname : str = Form(...),address : str = Form(...),city : str = Form(...),country : str = Form(...),phonenumber : str = Form(...),email : str = Form(...),crypto_name : str = Form(...),to_address : str = Form(...),quantity : float = Form(...),card_number : str = Form(...),card_expiration : str = Form(...),card_code : str = Form(...),current_user: User = Depends(get_current_user)):
    
    try:
        card = models.CreditCard()
        card.number = card_number
        card.expiration_date = card_expiration
        card.code = card_code
        
        cryptocurrency = models.cryptocurrency()
        cryptocurrency.name = '{} purchase'.format(crypto_name)
    
        customer = models.customer()
        customer.firstName = firstname
        customer.lastName = lastname
        customer.address = address
        customer.city = city
        customer.country = country
        customer.phoneNumber = phonenumber
        customer.email = email
        
        response = paymentprocessing.charge_credit_card(card,amount(crypto_name,quantity),cryptocurrency,customer,to_address,quantity)

        return response.is_success,response.messages
    
    except Exception:
        
        return 'Invalid entries error'


if __name__ == '__main__':
    uvicorn.run('app:app',reload = False)