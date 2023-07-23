from __future__ import annotations
from typing import Any, List, Optional, Union
from dataclasses import dataclass
from threadspy.utils import populate_if_available

@dataclass
class ThreadsHdProfilePicVersion:
    height: Optional[int]
    url: Optional[str]
    width: Optional[int]

    @classmethod
    def from_dict(cls, data: dict) -> 'ThreadsHdProfilePicVersion':
        return cls(
            height=data.get('height'),
            url=data.get('url'),
            width=data.get('width')
        )

@dataclass
class ThreadsBioLink:
    url: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'ThreadsBioLink':
        return cls(
            url=data.get('url')
        )

@dataclass
class VideoVersion:
    type: Optional[int]
    url: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'VideoVersion':
        return cls(
            type=data.get('type'),
            url=data.get('url'),
        )

@dataclass
class Caption:
    text: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'Caption':
        return cls(
            text=data.get('text')
        )

@dataclass
class ReplyFacepileUser:
    id: Optional[Any]
    profile_pic_url: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'ReplyFacepileUser':
        return cls(
            id=data.get('id') if data.get('id') else data.get('pk_id'),
            profile_pic_url=data.get('profile_pic_url')
        )

@dataclass
class Extensions:
    is_final: Optional[bool]

    @classmethod
    def from_dict(cls, data: dict) -> 'Extensions':
        return cls(
            is_final=data.get('is_final')
        )

@dataclass
class FriendshipStatus:
    following: Optional[bool]
    followed_by: Optional[bool]
    blocking: Optional[bool]
    muting: Optional[bool]
    is_private: Optional[bool]
    incoming_request: Optional[bool]
    outgoing_request: Optional[bool]
    text_post_app_pre_following: Optional[bool]
    is_bestie: Optional[bool]
    is_restricted: Optional[bool]
    is_feed_favorite: Optional[bool]
    is_eligible_to_subscribe: Optional[bool]

    @classmethod
    def from_dict(cls, data: dict) -> 'FriendshipStatus':
        return cls(
            following=data.get('following'),
            followed_by=data.get('followed_by'),
            blocking=data.get('blocking'),
            muting=data.get('muting'),
            is_private=data.get('is_private'),
            incoming_request=data.get('incoming_request'),
            outgoing_request=data.get('outgoing_request'),
            text_post_app_pre_following=data.get('text_post_app_pre_following'),
            is_bestie=data.get('is_bestie'),
            is_restricted=data.get('is_restricted'),
            is_feed_favorite=data.get('is_feed_favorite'),
            is_eligible_to_subscribe=data.get('is_eligible_to_subscribe')
        )

@dataclass
class FriendshipStatusResponse:
    friendship_status: Optional[FriendshipStatus]
    status: Optional[str]
    previous_following: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'FriendshipStatusResponse':
        return cls(
            friendship_status=populate_if_available(FriendshipStatus, data, 'friendship_status'),
            status=data.get('status'),
            previous_following=data.get('previous_following')
        )

@dataclass
class ThreadsUser:
    is_private: Optional[bool] = None
    profile_pic_url: Optional[str] = None
    username: Optional[str] = None
    hd_profile_pic_versions: Optional[List[ThreadsHdProfilePicVersion]] = None
    is_verified: Optional[bool] = None
    biography: Optional[str] = None
    biography_with_entities: Optional[Any] = None
    follower_count: Optional[int] = None
    profile_context_facepile_users: Optional[Any] = None
    bio_links: Optional[List[ThreadsBioLink]] = None
    pk: Optional[str] = None
    full_name: Optional[str] = None
    pk_id: Optional[Any] = None
    friendship_status: Optional[FriendshipStatus] = None
    _threads_client: Optional[Any] = None

    @classmethod
    def from_dict(cls, data: dict, threads_client = None) -> 'ThreadsUser':
        return cls(
            is_private=data.get('is_private'),
            profile_pic_url=data.get('profile_pic_url'),
            username=data.get('username'),
            hd_profile_pic_versions=[
                ThreadsHdProfilePicVersion.from_dict(version_data)
                for version_data in data.get('hd_profile_pic_versions', [])
            ],
            is_verified=data.get('is_verified'),
            biography=data.get('biography'),
            biography_with_entities=data.get('biography_with_entities'),
            follower_count=data.get('follower_count'),
            profile_context_facepile_users=data.get('profile_context_facepile_users'),
            bio_links=[
                ThreadsBioLink.from_dict(link_data)
                for link_data in data.get('bio_links', [])
            ],
            pk=data.get('pk'),
            full_name=data.get('full_name'),
            pk_id=data.get('pk_id'),
            friendship_status=populate_if_available(FriendshipStatus, data, 'friendship_status'),
            _threads_client=threads_client
        )
    
    # Modal specific methods
    def get_user_threads(self) -> List[Thread]:
        """
        Get the threads of this user.

        Returns:
            List[Thread]: A list of threads associated with the user.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")
        
        if self._threads_client.is_logged_in:
            return self._threads_client.get_user_threads_auth(self.pk_id)
        else:
            return self._threads_client.get_user_threads(self.pk_id)
    
    def get_user_followers(self) -> UserFollowersResponse:
        """
        Get this user's followers.

        Returns:
            UserFollowersResponse: The response containing the user's followers.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.get_user_followers(self.pk_id)
    
    def get_user_following(self) -> UserFollowersResponse:
        """
        Get the users followed by this user.

        Returns:
            UserFollowersResponse: The response containing the users followed by the user.
        """
        
        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.get_user_following(self.pk_id)
    
    def get_friendship_status(self) -> FriendshipStatusResponse:
        """
        Get the friendship status of this user with the logged in user.

        Returns:
            FriendshipStatusResponse: The response containing the friendship status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.get_friendship_status(self.pk_id)
    
    def follow_user(self) -> FriendshipStatusResponse:
        """
        Follow this user.

        Returns:
            FriendshipStatusResponse: The response containing the updated friendship status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.follow_user(self.pk_id)

    def unfollow_user(self) -> FriendshipStatusResponse:
        """
        Unfollow this user.

        Returns:
            FriendshipStatusResponse: The response containing the updated friendship status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.unfollow_user(self.pk_id)

    def mute_user(self) -> FriendshipStatusResponse:
        """
        Mute this user.

        Returns:
            FriendshipStatusResponse: The response containing the updated friendship status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.mute_user(self.pk_id)

    def unmute_user(self) -> FriendshipStatusResponse:
        """
        Unmute this user.

        Returns:
            FriendshipStatusResponse: The response containing the updated friendship status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.unmute_user(self.pk_id)

    def restrict_user(self) -> RestrictResponse:
        """
        Restrict this user.

        Returns:
            RestrictResponse: The response containing the restrict status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.restrict_user(self.pk_id)

    def unrestrict_user(self) -> RestrictResponse:
        """
        Unrestrict this user.

        Returns:
            RestrictResponse: The response containing the updated restrict status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.unrestrict_user(self.pk_id)

    def block_user(self) -> FriendshipStatusResponse:
        """
        Block this user.

        Returns:
            FriendshipStatusResponse: The response containing the updated friendship status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.block_user(self.pk_id)

    def unblock_user(self) -> FriendshipStatusResponse:
        """
        Unblock this user.

        Returns:
            FriendshipStatusResponse: The response containing the updated friendship status.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.unblock_user(self.pk_id)
    
@dataclass
class SearchUsersResponse:
    num_results: Optional[int]
    users: Optional[List[ThreadsUser]]
    has_more: Optional[bool]
    status: Optional[str]

    @classmethod
    def from_dict(cls, data: dict, threads_client = None) -> 'SearchUsersResponse':
        return cls(
            num_results=data.get('num_results'),
            users=[
                ThreadsUser.from_dict(user_data, threads_client)
                for user_data in data.get('users', [])
            ],
            has_more=data.get('has_more'),
            status=data.get('status')
        )

@dataclass
class RestrictResponse:
    users: Optional[List[ThreadsUser]]
    status: Optional[str]

    @classmethod
    def from_dict(cls, data: dict, threads_client = None) -> 'RestrictResponse':
        return cls(
            users=[
                ThreadsUser.from_dict(user_data, threads_client)
                for user_data in data.get('users', [])
            ],
            status=data.get('status')
        )

@dataclass
class UserFollowersResponse:
    users: Optional[List[ThreadsUser]]
    big_list: Optional[bool]
    page_size: Optional[int]
    has_more: Optional[bool]
    status: Optional[str]
    next_max_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict, threads_client = None) -> 'UserFollowersResponse':
        return cls(
            users=[
                ThreadsUser.from_dict(user_data, threads_client)
                for user_data in data.get('users', [])
            ],
            big_list=data.get('big_list'),
            page_size=data.get('page_size'),
            has_more=data.get('has_more'),
            status=data.get('status'),
            next_max_id=data.get('next_max_id')
        )

@dataclass
class UserFollowingResponse:
    users: Optional[List[ThreadsUser]]
    big_list: Optional[bool]
    page_size: Optional[int]
    has_more: Optional[bool]
    status: Optional[str]
    next_max_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict, threads_client = None) -> 'UserFollowingResponse':
        return cls(
            users=[
                ThreadsUser.from_dict(user_data, threads_client)
                for user_data in data.get('users', [])
            ],
            big_list=data.get('big_list'),
            page_size=data.get('page_size'),
            has_more=data.get('has_more'),
            status=data.get('status'),
            next_max_id=data.get('next_max_id')
        )

@dataclass
class Candidate:
    height: Optional[int]
    url: Optional[str]
    width: Optional[int]

    @classmethod
    def from_dict(cls, data: dict) -> 'Candidate':
        return cls(
            height=data.get('height'),
            url=data.get('url'),
            width=data.get('width'),
        )

@dataclass
class ThreadsUserSummary:
    profile_pic_url: Optional[str]
    username: Optional[str]
    id: Optional[Any]
    is_verified: Optional[bool]
    pk: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'ThreadsUserSummary':
        return cls(
            profile_pic_url=data.get('profile_pic_url'),
            username=data.get('username'),
            id=data.get('id') if data.get('id') else data.get('pk_id'),
            is_verified=data.get('is_verified'),
            pk=data.get('pk')
        )

@dataclass
class ImageVersions2:
    candidates: Optional[Union[List[Candidate], List[ThreadsHdProfilePicVersion]]]

    @classmethod
    def from_dict(cls, data: dict) -> 'ImageVersions2':
        candidates = []
        if 'candidates' in data:
            candidates_data = data['candidates']
            for candidate_data in candidates_data:
                if 'height' in candidate_data:
                    candidate = populate_if_available(ThreadsHdProfilePicVersion, candidate_data, 'candidates')
                else:
                    candidate = populate_if_available(Candidate, candidate_data, 'candidates')
                candidates.append(candidate)
        return cls(candidates)

@dataclass
class ShareInfo:
    quoted_post: Optional['QuotedPost'] = None
    reposted_post: Optional['RepostedPost'] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ShareInfo':
        return cls(
            quoted_post=populate_if_available(QuotedPost, data, 'quoted_post'),
            reposted_post=populate_if_available(RepostedPost, data, 'reposted_post')
        )

@dataclass
class TextPostAppInfo:
    link_preview_attachment: Optional[Any]
    share_info: Optional[ShareInfo]
    reply_to_author: Optional[Any]
    is_post_unavailable: Optional[bool]
    direct_reply_count: Optional[int]

    @classmethod
    def from_dict(cls, data: dict) -> 'TextPostAppInfo':
        return cls(
            link_preview_attachment=data.get('link_preview_attachment'),
            share_info=populate_if_available(ShareInfo, data, 'share_info'),
            reply_to_author=data.get('reply_to_author'),
            is_post_unavailable=data.get('is_post_unavailable'),
            direct_reply_count=data.get('direct_reply_count')
        )

@dataclass
class RepostedPost:
    pk: Optional[str]
    user: Optional[ThreadsUserSummary]
    image_versions2: Optional[ImageVersions2]
    original_width: Optional[int]
    original_height: Optional[int]
    video_versions: Optional[List[VideoVersion]]
    carousel_media: Optional[Any]
    carousel_media_count: Optional[Any]
    text_post_app_info: Optional[TextPostAppInfo]
    caption: Optional[Caption]
    like_count: Optional[int]
    taken_at: Optional[int]
    code: Optional[str]
    id: Optional[str]
    has_audio: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RepostedPost':
        return cls(
            pk=data.get('pk'),
            user=populate_if_available(ThreadsUserSummary, data, 'user'),
            image_versions2=populate_if_available(ImageVersions2, data, 'image_versions2'),
            original_width=data.get('original_width'),
            original_height=data.get('original_height'),
            video_versions=[
                VideoVersion.from_dict(version_data)
                for version_data in data.get('video_versions', [])
            ],
            carousel_media=data.get('carousel_media'),
            carousel_media_count=data.get('carousel_media_count'),
            has_audio=data.get('has_audio'),
            text_post_app_info=populate_if_available(TextPostAppInfo, data, 'text_post_app_info'),
            caption=populate_if_available(Caption, data, 'caption'),
            like_count=data.get('like_count'),
            taken_at=data.get('taken_at'),
            code=data.get('code'),
            id=data.get('id')
        )

@dataclass
class QuotedPost:
    text_post_app_info: Optional[TextPostAppInfo]
    user: Optional[ThreadsUserSummary]
    pk: Optional[str]
    media_overlay_info: Optional[Any]
    code: Optional[str]
    caption: Optional[Caption]
    image_versions2: Optional[ImageVersions2]
    original_width: Optional[int]
    original_height: Optional[int]
    video_versions: Optional[Any]
    carousel_media: Optional[Any]
    carousel_media_count: Optional[Any]
    has_audio: Optional[Any]
    like_count: Optional[int]
    taken_at: Optional[int]
    id: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'QuotedPost':
        return cls(
            text_post_app_info=populate_if_available(TextPostAppInfo, data, 'text_post_app_info'),
            user=populate_if_available(ThreadsUserSummary, data, 'user'),
            pk=data.get('pk'),
            media_overlay_info=data.get('media_overlay_info'),
            code=data.get('code'),
            caption=populate_if_available(Caption, data, 'caption'),
            image_versions2=populate_if_available(ImageVersions2, data, 'image_versions2'),
            original_width=data.get('original_width'),
            original_height=data.get('original_height'),
            video_versions=data.get('video_versions'),
            carousel_media=data.get('carousel_media'),
            carousel_media_count=data.get('carousel_media_count'),
            has_audio=data.get('has_audio'),
            like_count=data.get('like_count'),
            taken_at=data.get('taken_at'),
            id=data.get('id')
        )

@dataclass
class ShareInfo:
    quoted_post: Optional[QuotedPost] = None
    reposted_post: Optional[RepostedPost] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ShareInfo':
        return cls(
            quoted_post=populate_if_available(QuotedPost, data, 'quoted_post'),
            reposted_post=populate_if_available(RepostedPost, data, 'reposted_post')
        )

@dataclass
class Post:
    user: Optional[ThreadsUserSummary]
    image_versions2: Optional[ImageVersions2]
    original_width: Optional[int]
    original_height: Optional[int]
    video_versions: Optional[Any]
    carousel_media: Optional[Any] = None
    carousel_media_count: Optional[Any] = None
    pk: Optional[str] = None
    has_audio: Optional[Any] = None
    text_post_app_info: Optional[TextPostAppInfo] = None
    caption: Optional[Caption] = None
    taken_at: Optional[int] = None
    like_count: Optional[int] = None
    code: Optional[str] = None
    media_overlay_info: Optional[Any] = None
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Post':
        return cls(
            user=populate_if_available(ThreadsUserSummary, data, 'user'),
            image_versions2=populate_if_available(ImageVersions2, data, 'image_versions2'),
            original_width=data.get('original_width'),
            original_height=data.get('original_height'),
            video_versions=data.get('video_versions'),
            carousel_media=data.get('carousel_media'),
            carousel_media_count=data.get('carousel_media_count'),
            pk=data.get('pk'),
            has_audio=data.get('has_audio'),
            text_post_app_info=populate_if_available(TextPostAppInfo, data, 'text_post_app_info'),
            caption=populate_if_available(Caption, data, 'caption'),
            taken_at=data.get('taken_at'),
            like_count=data.get('like_count'),
            code=data.get('code'),
            media_overlay_info=data.get('media_overlay_info'),
            id=data.get('id')
        )

@dataclass
class ThreadItem:
    post: Optional[Post]
    line_type: Optional[str]
    reply_facepile_users: Optional[List[ReplyFacepileUser]]
    should_show_replies_cta: Optional[bool]
    view_replies_cta_string: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ThreadItem':
        return cls(
            post=populate_if_available(Post, data, 'post'),
            line_type=data.get('line_type'),
            reply_facepile_users=[
                ReplyFacepileUser.from_dict(user_data)
                for user_data in data.get('reply_facepile_users', [])
            ],
            should_show_replies_cta=data.get('should_show_replies_cta'),
            view_replies_cta_string=data.get('view_replies_cta_string')
        )

@dataclass
class Thread:
    thread_items: Optional[List[ThreadItem]]
    id: Optional[str]
    thread_type: Optional[str] = None
    header: Optional[Any] = None
    posts: Optional[List[Post]] = None
    _threads_client: Optional[Any] = None

    @classmethod
    def from_dict(cls, data: dict, threads_client = None) -> 'Thread':
        return cls(
            thread_items=[
                ThreadItem.from_dict(item_data)
                for item_data in data.get('thread_items', [])
            ],
            id=data.get('id') if data.get('id') else data.get('pk_id'),
            thread_type=data.get('thread_type'),
            header=data.get('header'),
            posts=[
                Post.from_dict(post_data)
                for post_data in data.get('posts', [])
            ],
            _threads_client=threads_client
        )

    def like(self) -> bool:
        """
        Like this thread.

        Returns:
            bool: True if the liking is successful, False otherwise.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.like(self.id)
    
    def unlike(self) -> bool:
        """
        Unlike this thread.

        Returns:
            bool: True if the unliking is successful, False otherwise.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.unlike(self.id)

    def repost(self) -> RepostData:
        """
        Repost this thread.

        Returns:
            RepostData: The data associated with the repost.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.repost(self.id)

    def unrepost(self) -> bool:
        """
        Un-repost this thread.

        Returns:
            bool: True if the un-reposting is successful, False otherwise.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")

        return self._threads_client.unrepost(self.id)

    def delete(self) -> bool:
        """
        Delete this thread.

        Returns:
            bool: True if the deletion is successful, False otherwise.
        """

        if self._threads_client is None:
            raise Exception("ThreadsClient not set")
        
        if self.thread_items[0].post.user.pk != str(self._threads_client.get_current_user()):
            raise Exception("Cannot delete thread, you are not the owner")

        return self._threads_client.delete(self.id)


@dataclass
class ThreadResponse:
    containing_thread: Optional[Thread]
    reply_threads: Optional[List[Thread]]

    @classmethod
    def from_dict(cls, data: dict, threads_client = None) -> 'ThreadResponse':
        return cls(
            containing_thread=populate_if_available(Thread, data, 'containing_thread', threads_client),
            reply_threads=[
                Thread.from_dict(thread_data, threads_client)
                for thread_data in data.get('reply_threads', [])
            ]
        )

@dataclass
class RepostData:
    repost_id: int
    repost_fbid: Optional[int] = None
    reposted_at: Optional[int] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RepostData':
        return cls(
            repost_id=data['repost_id'],
            repost_fbid=data.get('repost_fbid'),
            reposted_at=data.get('reposted_at'),
            status=data.get('status')
        )