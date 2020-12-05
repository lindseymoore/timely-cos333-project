"""
A module with functions that are used to handle CAS authentication.
Code written by Professor Robert Dondero and published in associated COS333 lecture files.
"""

from urllib.request import urlopen
from urllib.parse import quote
from re import sub
from flask import request, session, redirect, abort


class CASClient:
    """Represents a client to handle CAS Authentication."""

    def __init__(self, url='https://fed.princeton.edu/cas/'):
        """
        Initialize a new CASClient object so it uses the given CAS
        server, or fed.princeton.edu if no server is given.
        """
        self.cas_url = url


    def strip_ticket(self):
        """
        Return the URL of the current request after stripping out the
        "ticket" parameter added by the CAS server.
        """
        url = request.url
        if url is None:
            return "something is badly wrong"
        url = sub(r'ticket=[^&]*&?', '', url)
        url = sub(r'\?&?$|&$', '', url)
        return url


    def validate(self, ticket):
        """
        Validate a login ticket by contacting the CAS server. If
        valid, return the user's username; otherwise, return None.
        """
        val_url = self.cas_url + "validate" + \
            '?service=' + quote(self.strip_ticket()) + \
            '&ticket=' + quote(ticket)
        read = urlopen(val_url).readlines()   # returns 2 lines
        if len(read) != 2:
            return None
        first_line = read[0].decode('utf-8')
        second_line = read[1].decode('utf-8')
        if not first_line.startswith('yes'):
            return None
        return second_line


    def authenticate(self):
        """
        Authenticate the remote user, and return the user's username.
        Do not return unless the user is successfully authenticated.
        """

        # If the user's username is in the session, then the user was
        # authenticated previously.  So return the user's username.
        if 'username' in session:
            return session.get('username')

        # If the request contains a login ticket, then try to
        # validate it.
        ticket = request.args.get('ticket')
        if ticket is not None:
            username = self.validate(ticket)
            if username is not None:
                # The user is authenticated, so store the user's
                # username in the session.
                session['username'] = username
                return username

        # The request does not contain a valid login ticket, so
        # redirect the browser to the login page to get one.
        login_url = self.cas_url + 'login' \
            + '?service=' + quote(self.strip_ticket())

        abort(redirect(login_url))


    def logout(self):
        """
        Logout the user.
        """

        # Delete the user's username from the session.
        session.pop('username')

        # Redirect the browser to the logout page.
        logout_url = self.cas_url + 'logout'
        abort(redirect(logout_url))


def main():
    """Inform the user that this module is not executable."""
    print("CASClient does not run standalone")


if __name__ == '__main__':
    main()
