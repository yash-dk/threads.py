# threads.py
Unofficial API for Threads by Instagram. With type hints.

# Installing
To install the library on Linux:

`python3 -m pip install threads.py`

To install the library on Windows:

`py -m pip install threads.py`

**Python 3.8 or higher is needed for the library**

> This library will be under active development so please raise the issue with your concerns and errors.


# Wrapper

## Available Methods
<details>
<summary>Expand</summary>

1. `login(self) -> bool`
   - Description: Logs in the user and obtains the private API token.
   - Returns: bool - True if login is successful, False otherwise.

2. `get_user_id(self, username: str, instagram: bool = False) -> int`
   - Description: Gets the user ID from either Threads or Instagram for the corresponding username.
   - Parameters:
     - username (str): The username to get the ID for.
     - instagram (bool, optional): If True, search for the user on Instagram. Default is False.
   - Returns: int - The user ID.

3. `get_user_profile(self, user_id: int) -> ThreadsUser`
   - Description: Gets the user profile for a given user ID.
   - Parameters:
     - user_id (int): The user ID.
   - Returns: ThreadsUser - The ThreadsUser object containing user profile information.

4. `search_user(self, query: str) -> SearchUsersResponse`
   - Description: Searches for users based on a query string provided.
   - Parameters:
     - query (str): The search query.
   - Returns: SearchUsersResponse - The response object containing search results.

5. `get_thread(self, user_id: int) -> ThreadResponse`
   - Description: Gets the thread information for a given thread ID.
   - Parameters:
     - user_id (int): The thread ID.
   - Returns: ThreadResponse - The response object containing thread information.

6. `get_user_threads(self, user_id: int) -> List[Thread]`
   - Description: Gets the threads associated with a user with the provided user ID.
   - Parameters:
     - user_id (int): The user ID.
   - Returns: List[Thread] - A list of Thread objects.

7. `get_user_followers(self, user_id: int) -> UserFollowersResponse`
   - Description: Gets the followers of a user with the provided user ID.
   - Parameters:
     - user_id (int): The user ID.
   - Returns: UserFollowersResponse - The response object containing follower information.

8. `get_user_following(self, user_id: int) -> UserFollowingResponse`
   - Description: Gets the users a user is following.
   - Parameters:
     - user_id (int): The user ID.
   - Returns: UserFollowingResponse - The response object containing following information.

9. `get_friendship_status(self, user_id: int) -> FriendshipStatusResponse`
   - Description: Gets the friendship status with another user.
   - Parameters:
     - user_id (int): The user ID.
   - Returns: FriendshipStatusResponse - The response object containing friendship status.

10. `follow_user(self, user_id: int) -> FriendshipStatusResponse`
    - Description: Follows a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: FriendshipStatusResponse - The response object containing friendship status after following.

11. `unfollow_user(self, user_id: int) -> FriendshipStatusResponse`
    - Description: Unfollows a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: FriendshipStatusResponse - The response object containing friendship status after unfollowing.

12. `mute_user(self, user_id: int) -> FriendshipStatusResponse`
    - Description: Mutes a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: FriendshipStatusResponse - The response object containing friendship status after muting.

13. `unmute_user(self, user_id: int) -> FriendshipStatusResponse`
    - Description: Unmutes a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: FriendshipStatusResponse - The response object containing friendship status after unmuting.

14. `restrict_user(self, user_id: int) -> RestrictResponse`
    - Description: Restricts a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: RestrictResponse - The response object containing restrict status.

15. `unrestrict_user(self, user_id: int) -> RestrictResponse`
    - Description: Unrestricts a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: RestrictResponse - The response object containing restrict status after unrestricting.

16. `block_user(self, user_id: int) -> FriendshipStatusResponse`
    - Description: Blocks a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: FriendshipStatusResponse - The response object containing friendship status after blocking.

17. `unblock_user(self, user_id: int) -> FriendshipStatusResponse`
    - Description: Unblocks a user with the provided user ID.
    - Parameters:
      - user_id (int): The user ID.
    - Returns: FriendshipStatusResponse - The response object containing friendship status after unblocking.

18. `like(self, thread_id: int) -> bool`
    - Description: Likes a thread with the provided thread ID.
    - Parameters:
      - thread_id (int): The ID of the thread to like.
    - Returns: bool - True if the like is successful, False otherwise.

19. `unlike(self, thread_id: int) -> bool`
    - Description: Unlikes a thread with the provided thread ID.
    - Parameters:
      - thread_id (int): The ID of the thread to unlike.
    - Returns: bool - True if the unlike is successful, False otherwise.

20. `repost(self, thread_id: int) -> RepostData`
    - Description: Reposts a thread with the provided thread ID.
    - Parameters:
      - thread_id (int): The ID of the thread to repost.
    - Returns: RepostData - The response object containing repost data.

21. `unrepost(self, original_thread_id: int) -> bool`
    - Description: Unreposts a thread with the provided original thread ID.
    - Parameters:
      - thread_id (int): The ID of the original thread to unrepost.
    - Returns: bool - True if the unrepost is successful, False otherwise.

22. `delete(self, thread_id: int) -> bool`
    - Description: Deletes a thread with the provided thread ID.
    - Parameters:
      - thread_id (int): The ID of the thread to delete.
    - Returns: bool - True if the deletion is successful, False otherwise.

23. `create(self, text: str, url: str = None, image: Optional[Union[str, List]] = None, reply_to: int = None) -> dict`
    - Description: Creates a new thread.
    - Parameters:
        - text (str): The text content of the thread.
        - url (str, optional): The URL to include in the thread. Default is None.
        - image (str or list, optional): The image or list of images to include in the thread. Default is None.
        - reply_to (int, optional): The ID of the thread to reply to. Default is None.
    - Returns: dict - The response JSON containing the details of the newly created thread.

</details>

## Customized Types

<details>
<summary>Expand</summary>

## 1. Threads User

1. **get_user_threads() -> List[Thread]**
   - Returns: List[Thread]
   - Description: Get the threads of this user.

2. **get_user_followers() -> UserFollowersResponse**
   - Returns: UserFollowersResponse
   - Description: Get this user's followers.

3. **get_user_following() -> UserFollowingResponse**
   - Returns: UserFollowingResponse
   - Description: Get the users followed by this user.

4. **get_friendship_status() -> FriendshipStatusResponse**
   - Returns: FriendshipStatusResponse
   - Description: Get the friendship status of this user with the logged-in user.

5. **follow_user() -> FriendshipStatusResponse**
   - Returns: FriendshipStatusResponse
   - Description: Follow this user.

6. **unfollow_user() -> FriendshipStatusResponse**
   - Returns: FriendshipStatusResponse
   - Description: Unfollow this user.

7. **mute_user() -> FriendshipStatusResponse**
   - Returns: FriendshipStatusResponse
   - Description: Mute this user.

8. **unmute_user() -> FriendshipStatusResponse**
   - Returns: FriendshipStatusResponse
   - Description: Unmute this user.

9. **restrict_user() -> RestrictResponse**
    - Returns: RestrictResponse
    - Description: Restrict this user.

10. **unrestrict_user() -> RestrictResponse**
    - Returns: RestrictResponse
    - Description: Unrestrict this user.

11. **block_user() -> FriendshipStatusResponse**
    - Returns: FriendshipStatusResponse
    - Description: Block this user.

12. **unblock_user() -> FriendshipStatusResponse**
    - Returns: FriendshipStatusResponse
    - Description: Unblock this user.

## 2. Thread

1. `like`
   - Returns: `bool`
   - Description: Likes this thread. Returns `True` if the liking is successful, `False` otherwise.

2. `unlike`
   - Returns: `bool`
   - Description: Unlikes this thread. Returns `True` if the unliking is successful, `False` otherwise.

3. `repost`
   - Returns: `RepostData`
   - Description: Reposts this thread. Returns the data associated with the repost.

4. `unrepost`
   - Returns: `bool`
   - Description: Un-reposts this thread. Returns `True` if the un-reposting is successful, `False` otherwise.

5. `delete`
   - Returns: `bool`
   - Description: Deletes this thread. Returns `True` if the deletion is successful, `False` otherwise.

</details>



# Example

It is very easy to work with this library everything is type hinted and the names are straight forward, also go through the above Customized Types section to use this library efficiently. Here is a small example.

    import threadspy
    import os

    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")


    threads_api = threadspy.ThreadsApi(USERNAME, PASSWORD)
    login_status = threads_api.login()

    if login_status:
        user_id = threads_api.get_user_id('zuck')    # Get the user id of zuck
        
        zuck = threads_api.get_user_profile(user_id) # Get the user profile of zuck
        
        zuck.follow_user()                           # Follow zuck (Customized type)
        
        zuck_threads = zuck.get_user_threads()       # Get the threads of zuck

        for thread in zuck_threads[:3]:              # Like the first 3 threads of zuck
            thread.like()
            print(f"Liked thread with ID: {thread.id} and Caption: {thread.posts[0].caption.text}" )
    else:
        print("Login failed")

> ⚠️ Be cautious and try the library with your Alt Account. There is always risk of getting banned.  

# Important Concept
## Settings and Threads Token

- Settings is a json file that store the settings that were used to login using the provided.
- threads_token is the unique token that is obtained after logging in and is used for the subsequent requests.

`threads_api = threadspy.ThreadsApi(USERNAME, PASSWORD, settings_file="/path/to/settings", token_path="/path/to/token")`

Its a good idea to provide these paths, but if not provided then the `settings.json` and `threads_token.bin` will be store in the directory from where the code is run.

# Roadmap

- [ ] Implement remaining methods
  - [ ] Post ID from Thread ID
  - [ ] Thread Likers
  - [ ] Timeline
  - [ ] User Profile Replies
- [ ] Implement all the test cases
- [ ] Investigate 2FA login
- [ ] Seperate public and private API
- [ ] Own login flow instead of just depending on instagrapi