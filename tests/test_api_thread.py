from threadspy import ThreadsApi

def test_search_user(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True

    search_result = threads_api.search_user('zuck')
    
    assert search_result.num_results > 0
    assert len(search_result.users) > 0

def test_get_thread(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True
    thread_id = '3138977881796614961'

    thread = threads_api.get_thread(thread_id)

    assert thread.containing_thread.id == thread_id
    # Not needed but XD
    assert thread.containing_thread.posts[0].caption.text.startswith("Let's do this.")
    
def test_get_user_threads(threads_api: ThreadsApi):
    
    user_id = 314216
    user_threads = threads_api.get_user_threads(user_id)

    assert len(user_threads) > 0

def test_get_user_threads_auth(threads_api: ThreadsApi):
    if not threads_api.is_logged_in:
        result = threads_api.login()
        assert result == True
    
    user_id = 314216
    user_threads = threads_api.get_user_threads_auth(user_id)

    assert len(user_threads) > 0

