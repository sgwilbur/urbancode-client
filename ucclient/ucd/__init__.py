
class ucdclient( ucclient ):

    def __init__(self, base_url, user, password ):
      self._DEBUG = False

      self.session_key_header = 'UCD_SESSION_KEY'
