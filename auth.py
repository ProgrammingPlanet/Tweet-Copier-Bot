def sign_up(app, API, users):
    auth_url = app.get_authorization_url()
    print('visit this url to get pin: {}'.format(auth_url))
    while True:
        auth_pin = input('Enter PIN: ')
        try:
            access_token,access_token_secret = app.get_access_token(auth_pin)
            break
        except Exception as e:
            if 'Invalid oauth_verifier' in str(e):
                print('Wrong Pin, Try Again...')
            else:
                print('unknow error')
                return None, None
    app.set_access_token(access_token,access_token_secret)
    api = API(app)
    user = api.me()
    users.update({
        user.id_str: {
            'username': user.screen_name,
            'access_token': access_token,
            'access_token_secret': access_token_secret,
            'copies': {}
        }
    })
    return api, users

def sign_in(app, users: dict, user_id: str):
    if str(user_id) in users:
        access_token,access_token_secret = users[user_id]['access_token'], users[user_id]['access_token_secret']
    else:
        print('sign up first')
        return
    app.set_access_token(access_token,access_token_secret)
    return app

def post_tweet(api, text):
    api.update_status(status=text)
    print('bot tweeted: {}'.format(_text))