from threadspy.constants import ENDPOINTS
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException
import re
from threadspy.models import *
from threadspy.utils import get_default_headers
from threadspy.auth import Authorization, Settings
import mimetypes
import json
from urllib.parse import quote
import random
import time
from uuid import uuid4
import os
from http import HTTPStatus
from typing import List, Optional, Union

class ThreadsApi:
    def __init__(
            self,
            username: str = None,
            password: str = None,
            timeout: int = 10,
            retries: int = 3,
            token_path: str = "threads_token.bin",
            settings_file: str = "settings.json"
    ):
        """
        Initializes the ThreadsApi class.

        Parameters:
            username (str, optional): The username for threads account. Default is None.
            password (str, optional): The password for threads account. Default is None.
            timeout (int, optional): The request timeout in seconds. Default is 10.
            retries (int, optional): The number of retries for failed requests. Default is 3.
            token_path (str, optional): The file path to save the authentication token. Default is "threads_token.bin".
            settings_file (str, optional): The file path to save the settings. Default is "settings.json".
        """

        self.timeout = timeout
        self.retries = retries
        self.session = self._create_session()
        
        self.public_token = None
        self.private_token = None
        self.is_logged_in = False
        self.user_id = None
        self.settings: Settings = None
        self.settings_file = settings_file
        self._load_settings()
        self.auth = Authorization(
            username=username,
            password=password,
            token_path=token_path,
            settings=self.settings
        )

    @property
    def get_public_headers(self):
        """
        Property to get headers for public API requests.

        Returns:
            dict: The headers with public API token.
        """

        headers = get_default_headers()
        self.public_token = self.auth.get_public_api_token()
        headers['X-FB-LSD'] = self.public_token
        return headers

    @property
    def get_private_headers(self):
        """
        Property to get headers for private API requests.

        Returns:
            dict: The headers with private API token and other required headers.
        """

        headers = get_default_headers()
        headers.update({
            'Authorization': f'Bearer IGT:2:{self.private_token}',
            'User-Agent': 'Barcelona 289.0.0.77.109 Android',
            'Sec-Fetch-Site': 'same-origin',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })

        return headers

    def _save_settings(self):
        """
        Internal method to save settings to a file.
        """

        with open(self.settings_file, 'w') as file:
            file.write(json.dumps(self.settings.to_dict(), indent=4))

    def _load_settings(self):
        """
        Internal method to load settings from a file.
        """

        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as file:
                self.settings = Settings.from_dict(json.loads(file.read()))
        else:
            self.settings = None 
    
    def _create_session(self) -> requests.Session:
        """
        Internal method to create a requests session with retry mechanism.

        Returns:
            requests.Session: The requests session object.
        """

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
        """
        Internal method to make a HTTP request and handle exceptions.

        Parameters:
            method (str): The HTTP method (GET, POST, PUT, DELETE).
            url (str): The URL to make the request.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            requests.Response: The response object.
        """

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except RequestException as exception:
            print(f"Error: {exception}")
            return None

    def _verify_login(self):
        """
        Internal method to verify user login. By fetching the usernameinfo.

        Returns:
            bool: True if login is successful, False otherwise.
        """

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
        """
        Logs in the user and obtains the private API token.

        Returns:
            bool: True if login is successful, False otherwise.
        """

        self.private_token = self.auth.get_instagram_api_token()
        if not self._verify_login():
            self.private_token = self.auth.get_instagram_api_token(refresh=True)
            if not self._verify_login():
                raise Exception("Login failed :(")
            else:
                self.is_logged_in = True
        else:
            self.is_logged_in = True

        self.settings = self.auth.get_settings()
        if self.is_logged_in and self.settings is not None:
            self._save_settings()

        return self.is_logged_in
    
    def get_user_id(self, username: str, instagram: bool = False) -> int:
        """
        Gets the user ID from either Threads or Instagram for the corresponding username.

        Parameters:
            username (str): The username to get the ID for.
            instagram (bool, optional): If True, search for the user on Instagram. Default is False.

        Returns:
            int: The user ID.
        """

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
        """
        Gets the ID of the current user.

        Returns:
            int: The user ID.
        """

        if self.user_id is not None:
            return self.user_id
        return self.get_user_id(self.auth.username)
    
    def get_user_id_from_instagram(self, username: str) -> int:
        """
        Gets the user ID from Instagram for the corresponding username.

        Parameters:
            username (str): The username to get the ID for.

        Returns:
            int: The user ID.
        """

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
        """
        Gets the user ID from Threads for the corresponding username.

        Parameters:
            username (str): The username to get the ID for.

        Returns:
            int: The user ID.
        """

        url = ENDPOINTS.THREADS_BASE + f'/@{username}'
        response = self._request(
            method='GET',
            url=url,
            headers=self.get_public_headers
        )
        
        user_id_key_value = re.search('"user_id":"(\\d+)"', response.text).group()
        user_id = re.search('\\d+', user_id_key_value).group()

        return int(user_id)

    def get_user_profile(self, user_id: int) -> ThreadsUser:
        """
        Gets the user profile for a given user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            ThreadsUser: The ThreadsUser object containing user profile information.
        """

        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/users/{user_id}/info/',
            headers=self.get_private_headers
        )
        return ThreadsUser.from_dict(response.json()["user"], self)

    def search_user(self, query: str) -> SearchUsersResponse:
        """
        Searches for users based on a query string provided.

        Parameters:
            query (str): The search query.

        Returns:
            SearchUsersResponse: The response object containing search results.
        """

        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/users/search/?q={query}',
            headers=self.get_private_headers,
        )

        return SearchUsersResponse.from_dict(response.json(), self)

    def get_thread(self, user_id: int) -> ThreadResponse:
        """
        Gets the thread information for a given thread ID.

        Parameters:
            id (int): The thread ID.

        Returns:
            ThreadResponse: The response object containing thread information.
        """

        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/text_feed/{user_id}/replies',
            headers=self.get_private_headers,
        )

        return ThreadResponse.from_dict(response.json(), self)

    def get_user_threads(self, user_id: int) -> List[Thread]:
        """
        Gets the threads associated with a user with provided user ID.

        Parameters:
            user_id (int): The user ID.

        Returns:
            List[Thread]: A list of Thread objects.
        """

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

        return [Thread.from_dict(thread_data, self) for thread_data in response.json().get('threads', [])]
        
    def get_user_threads_auth(self, user_id: int) -> List[Thread]:
        """
        Gets the threads associated with a user with provided user ID using authenticated request.

        Parameters:
            user_id (int): The user ID.

        Returns:
            List[Thread]: A list of Thread objects.
        """

        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/text_feed/{user_id}/profile/',
            headers=self.get_private_headers
        )

        return [Thread.from_dict(thread_data, self) for thread_data in response.json().get('threads', [])]

    def get_user_followers(self, user_id: int) -> UserFollowersResponse:
        """
        Gets the followers of a user with the provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            UserFollowersResponse: The response object containing follower information.
        """

        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/{user_id}/followers/',
            headers=self.get_private_headers,
        )

        return UserFollowersResponse.from_dict(response.json(), self)
    
    def get_user_following(self, user_id: int) -> UserFollowingResponse:
        """
        Gets the users a user is following.

        Parameters:
            id (int): The user ID.

        Returns:
            UserFollowingResponse: The response object containing following information.
        """

        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/{user_id}/following/',
            headers=self.get_private_headers,
        )

        return UserFollowingResponse.from_dict(response.json(), self)

    def get_friendship_status(self, user_id: int) -> FriendshipStatusResponse:
        """
        Gets the friendship status with another user.

        Parameters:
            id (int): The user ID.

        Returns:
            FriendshipStatusResponse: The response object containing friendship status.
        """

        response = self._request(
            method='GET',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/show/{user_id}/',
            headers=self.get_private_headers,
        )
        
        # The response of the api is bit diferent need to handle that
        data = response.json()
        new_data = {
            'friendship_status': data,
            'status': data.get('status')
        }

        return FriendshipStatusResponse.from_dict(new_data)

    def follow_user(self, user_id: int) -> FriendshipStatusResponse:
        """
        Follows a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            FriendshipStatusResponse: The response object containing friendship status after following.
        """

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/create/{user_id}/',
            headers=self.get_private_headers,
        )

        return FriendshipStatusResponse.from_dict(response.json())
    
    def unfollow_user(self, user_id: int) -> FriendshipStatusResponse:
        """
        Unfollows a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            FriendshipStatusResponse: The response object containing friendship status after unfollowing.
        """

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/destroy/{user_id}/',
            headers=self.get_private_headers,
        )

        return FriendshipStatusResponse.from_dict(response.json())
    
    def mute_user(self, user_id: int) -> FriendshipStatusResponse:
        """
        Mutes a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            FriendshipStatusResponse: The response object containing friendship status after muting.
        """

        parameters = json.dumps(
            obj={
                'target_posts_author_id': user_id,
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

    def unmute_user(self, user_id: int) -> FriendshipStatusResponse:
        """
        Unmutes a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            FriendshipStatusResponse: The response object containing friendship status after unmuting.
        """

        parameters = json.dumps(
            obj={
                'target_posts_author_id': user_id,
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

    def restrict_user(self, user_id: int) -> RestrictResponse:
        """
        Restricts a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            RestrictResponse: The response object containing restrict status.
        """
        
        parameters = json.dumps(
            obj={
                'user_ids': user_id,
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

        return RestrictResponse.from_dict(response.json(), self)

    def unrestrict_user(self, user_id: int) -> RestrictResponse:
        """
        Unrestricts a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            RestrictResponse: The response object containing restrict status after unrestricting.
        """

        parameters = json.dumps(
            obj={
                'target_user_id': user_id,
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

        return RestrictResponse.from_dict(response.json(), self)

    def block_user(self, user_id: int) -> FriendshipStatusResponse:
        """
        Blocks a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            FriendshipStatusResponse: The response object containing friendship status after blocking.
        """

        parameters = json.dumps(
            obj={
                'user_id': user_id,
                'surface': 'ig_text_feed_timeline',
                'is_auto_block_enabled': 'true',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/block/{user_id}/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return FriendshipStatusResponse.from_dict(response.json())

    def unblock_user(self, user_id: int) -> FriendshipStatusResponse:
        """
        Unblocks a user with provided user ID.

        Parameters:
            id (int): The user ID.

        Returns:
            FriendshipStatusResponse: The response object containing friendship status after unblocking.
        """

        parameters = json.dumps(
            obj={
                'user_id': user_id,
                'container_module': 'ig_text_feed_timeline',
            },
        )

        encoded_parameters = quote(string=parameters, safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}/friendships/unblock/{user_id}/',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return FriendshipStatusResponse.from_dict(response.json())

    def like(self, thread_id: int) -> bool:
        """
        Likes a thread with provided thread ID.

        Parameters:
            thread_id (int): The ID of the thread to like.

        Returns:
            bool: True if the like is successful, False otherwise.
        """
        response = self._request(
            method="POST",
            url=f'{ENDPOINTS.INSTA_API_BASE}/media/{thread_id}_{self.user_id}/like/',
            headers=self.get_private_headers,
        )
        
        return response.json().get('status') == 'ok'

    def unlike(self, thread_id: int) -> bool:
        """
        Unlikes a thread with provided thread ID.

        Parameters:
            thread_id (int): The ID of the thread to unlike.

        Returns:
            bool: True if the unlike is successful, False otherwise.
        """

        response = self._request(
            method="POST",
            url=f'{ENDPOINTS.INSTA_API_BASE}/media/{thread_id}_{self.user_id}/unlike/',
            headers=self.get_private_headers,
        )

        return response.json().get('status') == 'ok'

    def repost(self, thread_id: int) -> RepostData:
        """
        Reposts a thread with provided thread ID.

        Parameters:
            thread_id (int): The ID of the thread to repost.

        Returns:
            RepostData: The response object containing repost data.
        """

        response = self._request(
            method="POST",
            url=f'{ENDPOINTS.INSTA_API_BASE}/repost/create_repost/',
            headers=self.get_private_headers,
            data=f'media_id={thread_id}',
        )

        return RepostData.from_dict(response.json())

    def unrepost(self, original_thread_id: int) -> bool:
        """
        Unreposts a thread with provided original thread ID.

        Parameters:
            thread_id (int): The ID of the original thread to unrepost.

        Returns:
            bool: True if the unrepost is successful, False otherwise.
        """
        
        response = self._request(
            method="POST",
            url=f'{ENDPOINTS.INSTA_API_BASE}/repost/delete_text_app_repost/',
            headers=self.get_private_headers,
            data=f'original_media_id={original_thread_id}',
        )

        return response.json().get('status') == 'ok'

    def delete(self, thread_id: int) -> bool:
        """
        Deletes a thread with provided thread ID.

        Parameters:
            thread_id (int): The ID of the thread to delete.

        Returns:
            bool: True if the deletion is successful, False otherwise.
        """

        response = self._request(
            method="POST",
            url=f'{ENDPOINTS.INSTA_API_BASE}/media/{thread_id}_{self.user_id}/delete/?media_type=TEXT_POST',
            headers=self.get_private_headers,
        )

        return response.json().get('status') == 'ok'

    def create(self, text: str, url: str=None, image: Optional[Union[str, List]]=None, reply_to: int=None) -> dict:
        """
        Creates a new thread.

        Parameters:
            text (str): The text content of the thread.
            url (str, optional): The URL to include in the thread. Default is None.
            image (str or list, optional): The image or list of images to include in the thread. Default is None.
            reply_to (int, optional): The ID of the thread to reply to. Default is None.

        Returns:
            dict: The response JSON containing the details of the newly created thread.

        TODO:
            return a thread object or create thread response
        """
        
        current_timestamp = time.time()
        timezone_offset = self.settings.timezone_offset

        parameters_as_string = {
            'text_post_app_info': {
                'reply_control': 0,
            },
            'timezone_offset': str(timezone_offset),
            'source_type': '4',
            'caption': text,
            '_uid': self.user_id,
            'device_id': self.settings.uuids["android_device_id"],
            'upload_id': int(current_timestamp),
            'device': {
                "manufacturer": self.settings.device_settings["manufacturer"],
                "model": self.settings.device_settings["model"],
                "android_version": self.settings.device_settings["android_version"],
                "android_release": self.settings.device_settings["android_release"],
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
            if len(image) == 1:
                image = image[0]
            elif len(image) < 1:
                raise Exception("No image provided")

            if isinstance(image, str):
                endpoint = "/media/configure_text_post_app_feed/"           
                upload_id = self._upload_image(image)
                if upload_id is None:
                    return False
                parameters_as_string["upload_id"] = upload_id
                parameters_as_string["scene_capture_type"] = ""
            elif isinstance(image, list):
                endpoint = "/media/configure_text_post_app_sidecar/"
                parameters_as_string['client_sidecar_id'] = int(time.time() * 1000)
                parameters_as_string["children_metadata"] = []
                for i in image:
                    upload_id = self._upload_image(i)
                    parameters_as_string["children_metadata"] += [{
                        'upload_id': upload_id,
                        'source_type': '4',
                        'timezone_offset': str(timezone_offset),
                        'scene_capture_type': "",
                    }]

        else:
            raise ValueError('Invalid image or url provided.')

        encoded_parameters = quote(string=json.dumps(obj=parameters_as_string), safe="!~*'()")

        response = self._request(
            method='POST',
            url=f'{ENDPOINTS.INSTA_API_BASE}{endpoint}',
            headers=self.get_private_headers,
            data=f'signed_body=SIGNATURE.{encoded_parameters}',
        )

        return response.json()
    
    def _upload_image(self, url: str) -> int:
        """
        Internal method to upload an image.

        Parameters:
            url (str): The URL or local file path of the image.

        Returns:
            int: The upload ID of the image.
        """

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