from urllib.parse import urlparse


def parse_uri(uri):
    """
    :param uri:
        example would be "mongodb://user:pencil@localhost:27017/admin?retryWrites=true&w=majority"
    :return: dict of the form
            {
                'nodelist': <list of (host, port) tuples>,
                'username': <username> or None,
                'password': <password> or None,
                'database': <database name> or None,
                'collection': <collection name> or None,
                'options': <dict of MongoDB URI options>,
                'fqdn': <fqdn of the MongoDB+SRV URI> or None
            }
    """
    parsed = urlparse(uri)
    username, password = None, None

    if "@" in parsed.netloc:
        user_password, host_port = parsed.netloc.split("@")
        username, password = user_password.split(":")
    else:
        host_port = parsed.netloc

    nodes = host_port.split(":")
    database = parsed.path if parsed.path != "/" else "admin"
    resp = {
        "nodelist": nodes,
        "username": username if username else None,
        "password": password if password else None,
        "database": database,
        "collection": None,
    }
    return resp
