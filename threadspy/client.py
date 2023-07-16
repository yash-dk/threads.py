from threadspy.constants import ENDPOINTS
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException
import re
from threadspy.models import *
from threadspy.utils import get_default_headers
from threadspy.auth import Authorization
import mimetypes
import json
from urllib.parse import quote
import random
import time
from uuid import uuid4
import os
from http import HTTPStatus
from datetime import datetime

class ThreadsApi:
    def __init__(
            self,
            username: str = None,
            password: str = None,
            timeout: int = 10,
            retries: int = 3,
    ):

        self.auth = Authorization(username, password)
        self.timeout = timeout
        self.retries = retries
        self.session = self._create_session()
        
        self.public_token = None
        self.private_token = None
        self.is_logged_in = False
        self.user_id = None

    @property
    def get_public_headers(self):
        headers = get_default_headers()
        self.public_token = self.auth.get_public_api_token()
        headers['X-FB-LSD'] = self.public_token
        return headers

    @property
    def get_private_headers(self):
        headers = get_default_headers()
        headers.update({
            'Authorization': f'Bearer IGT:2:{self.private_token}',
            'User-Agent': 'Barcelona 289.0.0.77.109 Android',
            'Sec-Fetch-Site': 'same-origin',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })

        return headers
         
    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=self.retries,
            backoff_factor="0.5",
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = self.timeout
        return session

    def _request(self, method, url, **kwargs) -> requests.Response:
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except RequestException as exception:
            print(f"Error: {exception}")
            return None

    def _verify_login(self):
        response = self._request(
            method='GET',
            url = f"{ENDPOINTS.INSTA_API_BASE}/users/{self.auth.username}/usernameinfo/",
            headers=self.get_private_headers
        )
        data = response.json()

        if any(
            (
                data.get('message') and data['message'] == "login_required",
                data.get('status') and data['status'] == 'fail',
            )
        ):
            if 'User not onboarded' in data.get('message', ''):
                raise Exception("User is not on threads.net :(")
            elif (
                'challenge_required' in data.get('message', '') and
                'challenge' in data and
                'url' in data['challenge'] and
                'https://www.instagram.com/accounts/suspended/' in data['challenge']['url']
            ):
                raise Exception("User is banned :(")
            
            return False
        
        self.user_id = int(data['user']['pk'])
        return True


    def login(self) -> bool:
        self.private_token = self.auth.get_instagram_api_token()
        if not self._verify_login():
            self.private_token = self.auth.get_instagram_api_token(refresh=True)
            if not self._verify_login():
                raise Exception("Login failed :(")
            else:
                self.is_logged_in = True
        else:
            self.is_logged_in = True

        return self.is_logged_in
    
    def get_user_id(self, username: str, instagram: bool = False) -> int:
        uid = None
        if instagram:
            uid = self.get_user_id_from_instagram(username)
            if uid is None:
                uid = self.get_user_id_from_threads(username)
        else:
            uid = self.get_user_id_from_threads(username)
            if uid is None:
                uid = self.get_user_id_from_instagram(username)
        
        return uid

    def get_current_user_id(self) -> int:
        if self.user_id is not None:
            return self.user_id
        return self.get_user_id(self.auth.username)
    
    def get_user_id_from_instagram(self, username: str) -> int:
        
        url = ENDPOINTS.INSTA_BASE + f'/{username}'
        response = self._request(
            method='GET',
            url=url,
            headers=self.get_public_headers
        )
        
        user_id_key_value = re.search('"user_id":"(\\d+)",', response.text).group()
        user_id = re.search('\\d+', user_id_key_value).group()

        return int(user_id)

    def get_user_id_from_threads(self, username: str) -> int:
        url = ENDPOINTS.THREADS_BASE + f'/@{username}'
        response = self._request(
            method='GET',
            url=url,
            headers=self.get_public_headers
        )
        
        user_id_key_value = re.search('"user_id":"(\\d+)"', response.text).group()
        user_id = re.search('\\d+', user_id_key_value).group()

        return int(user_id)

    def get_user_profile(self, id: int) -> ThreadsUser:
        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/users/{id}/info/',
            headers=self.get_private_headers
        )
        return ThreadsUser.from_dict(response.json()["user"])

    def search_user(self, query: str) -> SearchUsersResponse:
        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/users/search/?q={query}',
            headers=self.get_private_headers,
        )

        return SearchUsersResponse.from_dict(response.json())

    def get_thread(self, id: int) -> ThreadResponse:
        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/text_feed/{id}/replies',
            headers=self.get_private_headers,
        )

        return ThreadResponse.from_dict(response.json())

    def get_user_threads(self, user_id: int) -> List[Thread]:
        new_headers = self.get_public_headers

        new_headers.update({
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-fb-friendly-name': 'BarcelonaProfileThreadsTabQuery'
        })
        
        payload = {
                'lsd': self.public_token,
                'variables': json.dumps(
                    {
                        'userID': user_id,
                    }
                ),
                'doc_id': '6232751443445612'
            }
        response = self._request(
            method='POST',
            url=ENDPOINTS.THREADS_API_BASE,
            headers=new_headers,
            data=payload
        )

        return [Thread.from_dict(thread_data) for thread_data in response.json().get('threads', [])]
        
    def get_user_threads_auth(self, user_id: int) -> List[Thread]:
        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/text_feed/{user_id}/profile/',
            headers=self.get_private_headers
        )

        return [Thread.from_dict(thread_data) for thread_data in response.json().get('threads', [])]

    def get_user_followers(self, id: int) -> UserFollowersResponse:
        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/{id}/followers/',
            headers=self.get_private_headers,
        )

        return UserFollowersResponse.from_dict(response.json())
    
    def get_user_following(self, id: int) -> UserFollowingResponse:
        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/{id}/following/',
            headers=self.get_private_headers,
        )

        return UserFollowingResponse.from_dict(response.json())

    def get_friendship_status(self, id: int) -> FriendshipStatusResponse:
        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/show/{id}/',
            headers=self.get_private_headers,
        )
        
        # The response of the api is bit diferent need to handle that
        data = response.json()
        new_data = {
            'friendship_status': data,
            'status': data.get('status')
        }

        return FriendshipStatusResponse.from_dict(new_data)

    def follow_user(self, id: int) -> FriendshipStatusResponse:
        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/create/{id}/',
            headers=self.get_private_headers,
        )

        return FriendshipStatusResponse.from_dict(response.json())
    
    def unfollow_user(self, id: int) -> FriendshipStatusResponse:
        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/destroy/{id}/',
            headers=self.get_private_headers,
        )

        return FriendshipStatusResponse.from_dict(response.json())
    
    def mute_user(self, id: int) -> FriendshipStatusResponse:
        parameters = json.dumps(
            obj={
                'target_posts_author_id': id,
                'container_module': 'ig_text_feed_timeline',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/mute_posts_or_story_from_follow/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return FriendshipStatusResponse.from_dict(response.json())

    def unmute_user(self, id: int) -> FriendshipStatusResponse:
        parameters = json.dumps(
            obj={
                'target_posts_author_id': id,
                'container_module': 'ig_text_feed_timeline',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/unmute_posts_or_story_from_follow/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return FriendshipStatusResponse.from_dict(response.json())

    def restrict_user(self, id: int) -> RestrictResponse:
        parameters = json.dumps(
            obj={
                'user_ids': id,
                'container_module': 'ig_text_feed_timeline',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/restrict_action/restrict_many/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return RestrictResponse.from_dict(response.json())

    def unrestrict_user(self, id: int) -> RestrictResponse:
        parameters = json.dumps(
            obj={
                'target_user_id': id,
                'container_module': 'ig_text_feed_timeline',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/restrict_action/unrestrict/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return RestrictResponse.from_dict(response.json())

    def block_user(self, id: int) -> FriendshipStatusResponse:
        parameters = json.dumps(
            obj={
                'user_id': id,
                'surface': 'ig_text_feed_timeline',
                'is_auto_block_enabled': 'true',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/block/{id}/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return FriendshipStatusResponse.from_dict(response.json())

    def unblock_user(self, id: int) -> FriendshipStatusResponse:
        parameters = json.dumps(
            obj={
                'user_id': id,
                'container_module': 'ig_text_feed_timeline',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/unblock/{id}/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return FriendshipStatusResponse.from_dict(response.json())

    def create_thread(self, text, url=None, image=None, reply_to=None) -> dict:
        current_timestamp = time.time()
        timezone_offset = (datetime.now() - datetime.utcnow()).seconds

        parameters_as_string = {
            'text_post_app_info': {
                'reply_control': 0,
            },
            'timezone_offset': str(timezone_offset),
            'source_type': '4',
            'caption': text,
            '_uid': self.user_id,
            'device_id': str(f"android-{random.randint(0, 1e24):x}"),
            'upload_id': int(current_timestamp),
            'device': {
                "manufacturer": "OnePlus",
                "model": "ONEPLUS+A3010",
                "android_version": 25,
                "android_release": "7.1.1",
            }
        }

        if reply_to is not None:
            parameters_as_string['text_post_app_info']['reply_id'] = reply_to

        if url is None and image is None:
            endpoint = '/media/configure_text_only_post/'
            parameters_as_string['publish_mode'] = 'text_post'

        elif url is not None and image is None:
            endpoint = '/media/configure_text_only_post/'
            parameters_as_string['publish_mode'] = 'text_post'
            parameters_as_string['text_post_app_info']['link_attachment_url'] = url

        elif url is None and image is not None:
            endpoint = '/media/configure_text_post_app_feed/'
            parameters_as_string['upload_id'] = self._upload_image(url=image)
            parameters_as_string['scene_capture_type'] = ''

        else:
            raise ValueError('Provided image URL does not match required format. Please, create GitHub issue')

        encoded_parameters = quote(string=json.dumps(obj=parameters_as_string), safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}{endpoint}',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return response.json()
    
    def _upload_image(self, url: str) -> int:
        random_number = random.randint(1000000000, 9999999999)

        upload_id = int(time.time())
        upload_name = f'{upload_id}_0_{random_number}'

        url_pattern = re.compile("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

        file_data = None
        file_length = None
        mime_type = 'image/jpeg'
        waterfall_id = str(uuid4())

        is_url = True if re.match(url_pattern, url) is not None else False
        is_file_path = True if os.path.isfile(url) else False

        if is_file_path:
            with open(url, 'rb') as file:
                file_data = file.read()
                file_length = len(file_data)

            mime_type = mimetypes.guess_type(url)[0]

        elif is_url:
            response = self._request('GET', url, stream=True, timeout=2)
            content_type = response.headers.get("Content-Type")
            response.raw.decode_content = True
            mime_type = content_type.split(";")[0] if content_type else mime_type

            file_data = response.content
            file_length = len(response.content)
        else:
            raise ValueError('Wrong Image URL provided.')

        if file_data is None and file_length is None:
           raise ValueError("File is empty")

        parameters_as_string = {
            'media_type': 1,
            'upload_id': str(upload_id),
            'sticker_burnin_params': json.dumps([]),
            'image_compression': json.dumps(
                {
                    'lib_name': 'moz',
                    'lib_version': '3.1.m',
                    'quality': '80',
                },
            ),
            'xsharing_user_ids': json.dumps([]),
            'retry_context': json.dumps(
                {
                    'num_step_auto_retry': '0',
                    'num_reupload': '0',
                    'num_step_manual_retry': '0',
                },
            ),
            'IG-FB-Xpost-entry-point-v2': 'feed',
        }

        headers = self.get_private_headers
        headers.update({
            'Accept-Encoding': 'gzip',
            'X-Instagram-Rupload-Params': json.dumps(parameters_as_string),
            'X_FB_PHOTO_WATERFALL_ID': waterfall_id,
            'X-Entity-Type': mime_type,
            'Offset': '0',
            'X-Entity-Name': upload_name,
            'X-Entity-Length': str(file_length),
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(file_length),
        })

        response = self._request(
            method='POST',
            url=f'https://www.instagram.com/rupload_igphoto/{upload_name}',
            data=file_data,
            headers=headers,
        )

        if response.status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            raise ValueError('Image uploading has been failed. Please, create GitHub issue')

        return response.json().get('upload_id')