from threadspy import ThreadsApi

def test_get_user_followers(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    followers = threads_api.get_user_followers(314216)
    assert len(followers.users) > 0
    assert followers.status == 'ok'

def test_get_user_following(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    following = threads_api.get_user_following(314216)
    assert len(following.users) > 0
    assert following.status == 'ok'

def test_get_friendship_status(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    fsr = threads_api.get_friendship_status(314216)
    assert fsr.friendship_status.following == True
    assert fsr.friendship_status.followed_by == False

def test_follow_user(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    fsr = threads_api.follow_user(314216)
    assert fsr.friendship_status.following == True
    assert fsr.friendship_status.followed_by == False

def test_unfollow_user(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    fsr = threads_api.unfollow_user(314216)
    assert fsr.friendship_status.following == False
    assert fsr.friendship_status.followed_by == False