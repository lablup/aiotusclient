
def is_admin(session):
    return session.KeyPair(session.config.access_key).info()['is_admin']
