from threadspy import ThreadsApi

def test_login(threads_api: ThreadsApi):
    # Perform the login
    result = threads_api.login()

    # Check the result
    assert result == True