from threadspy import ThreadsApi
import os

def test_get_user_id(threads_api: ThreadsApi):
    # Perform the login
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    user_id = threads_api.get_user_id('zuck')
    
    assert user_id == 314216

def test_get_user_id_from_instagram(threads_api: ThreadsApi):
    # Perform the login
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    user_id = threads_api.get_user_id_from_instagram('zuck')
    
    assert user_id == 314216
    
def test_get_user_id_from_threads(threads_api: ThreadsApi):
    # Perform the login
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    user_id = threads_api.get_user_id_from_threads('zuck')
    
    assert user_id == 314216

def test_get_current_user_id(threads_api: ThreadsApi):
    # Perform the login
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    user_id = threads_api.get_current_user_id()
    
    assert user_id == int(os.getenv('USER_ID'))

def test_get_user_profile(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    user_profile = threads_api.get_user_profile(314216)
    assert user_profile.pk == 314216
    assert user_profile.username == 'zuck'
    
def test_search_user(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    search_result = threads_api.search_user('zuck')
    
    assert search_result.num_results > 0
    assert len(search_result.users) > 0