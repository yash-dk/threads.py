import requests
import re
from threadspy.utils import get_default_headers
import base64
from typing import Union
from instagrapi import Client
from cryptography.fernet import Fernet
import os

class Authorization:
    def __init__(
            self,
            username: str = None,
            password: str = None,
            token_path: str = "",
    ):
        self.username = username
        self.password = password
        self.token_path = token_path if token_path else "threads_token.bin"
        
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
        token = self._retrieve_token()
        if token is not None and not refresh:
            return token
        
        try:      
            iapi = Client()
            iapi.login(self.username, self.password)
            token = iapi.private.headers['Authorization'].split("Bearer IGT:2:")[1]
            self._store_token(token)
            return token
        except Exception as e:
            print(e)
            raise
    
    def get_public_api_token(self) -> str:
        response = requests.get(
            url='https://www.instagram.com/instagram',
            headers=self.headers,
        )

        token_key_value = re.search('LSD",\\[\\],{"token":"(.*?)"},\\d+\\]', response.text).group()
        token_key_value = token_key_value.replace('LSD",[],{"token":"', '')
        token = token_key_value.split('"')[0]

        return token