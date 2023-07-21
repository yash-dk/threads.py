import requests
import re
from threadspy.utils import get_default_headers
import base64
from typing import Union
from instagrapi import Client
from cryptography.fernet import Fernet
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    uuids: dict
    mid: str
    ig_u_rur: Optional[str]
    ig_www_claim: Optional[str]
    authorization_data: dict
    cookies: dict
    last_login: float
    device_settings: dict
    user_agent: str
    country: str
    country_code: int
    locale: str
    timezone_offset: int
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        return cls(
            uuids=data.get('uuids', {}),
            mid=data.get('mid', ''),
            ig_u_rur=data.get('ig_u_rur'),
            ig_www_claim=data.get('ig_www_claim'),
            authorization_data=data.get('authorization_data', {}),
            cookies=data.get('cookies', {}),
            last_login=data.get('last_login', 0.0),
            device_settings=data.get('device_settings', {}),
            user_agent=data.get('user_agent', ''),
            country=data.get('country', ''),
            country_code=data.get('country_code', 0),
            locale=data.get('locale', ''),
            timezone_offset=data.get('timezone_offset', 0)
        )

    def to_dict(self) -> dict:
        return {
            'uuids': self.uuids,
            'mid': self.mid,
            'ig_u_rur': self.ig_u_rur,
            'ig_www_claim': self.ig_www_claim,
            'authorization_data': self.authorization_data,
            'cookies': self.cookies,
            'last_login': self.last_login,
            'device_settings': self.device_settings,
            'user_agent': self.user_agent,
            'country': self.country,
            'country_code': self.country_code,
            'locale': self.locale,
            'timezone_offset': self.timezone_offset
        }


class Authorization:
    def __init__(
            self,
            username: str = None,
            password: str = None,
            token_path: str = "",
            settings: Settings = None,
    ):
        self.username = username
        self.password = password
        self.token_path = token_path if token_path else "threads_token.bin"
        self.settings = settings
        self.headers = get_default_headers()

    def generate_key_from_password(self, password):
        # Pad the password if its length is less than 32 bytes
        while len(password) < 32:
            password += password
        # Truncate the password if its length exceeds 32 bytes
        password = password[:32]
        # Convert the password to URL-safe base64 encoding
        key = base64.urlsafe_b64encode(password.encode())
        return key

    def _store_token(self, token):
        cipher_suite = Fernet(self.generate_key_from_password(self.password))
        encrypted_token = cipher_suite.encrypt(token.encode())
        with open(self.token_path, 'wb') as file:
            file.write(encrypted_token)

    def _retrieve_token(self):
        cipher_suite = Fernet(self.generate_key_from_password(self.password))
        if not os.path.exists(self.token_path):
            return None
        with open(self.token_path, 'rb') as file:
            encrypted_token = file.read()
        decrypted_token = cipher_suite.decrypt(encrypted_token)
        return decrypted_token.decode()


    def get_instagram_api_token(self, refresh: bool = False) -> Union[str, None]:
        # token = self._retrieve_token()
        token = None
        if token is not None and not refresh:
            return token
        
        try:      
            iapi = Client()
            if self.settings is not None:
                print("cached")
                iapi.set_settings(self.settings.to_dict())
                iapi.login(self.username, self.password)
            else:
                print("not cached")
                iapi.login(self.username, self.password)
                self.settings = Settings.from_dict(iapi.get_settings())
            
            token = iapi.private.headers['Authorization'].split("Bearer IGT:2:")[1]
            print(token)
            self._store_token(token)
            return token
        except Exception as e:
            print(e)
            raise
    
    def get_settings(self) -> Settings:
        return self.settings

    def get_public_api_token(self) -> str:
        response = requests.get(
            url='https://www.instagram.com/instagram',
            headers=self.headers,
        )

        token_key_value = re.search('LSD",\\[\\],{"token":"(.*?)"},\\d+\\]', response.text).group()
        token_key_value = token_key_value.replace('LSD",[],{"token":"', '')
        token = token_key_value.split('"')[0]

        return token