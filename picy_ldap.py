import sys
import ldap
from ldif import LDIFParser


class IC_Ldap(object):

    def __init__(self):
        self.conn = ldap.initialize('ldaps://unixldap.cc.ic.ac.uk')

    def bind(self):
        self.conn.simple_bind_s()

    def auth_bind(self, user, passw):

        if not user or not passw:
            print 'something empty'
            return False

        dn = 'uid=%s,ou=People,ou=everyone,dc=ic,dc=ac,dc=uk' % user

        try:
            # Bind OK
            self.conn.bind_s(dn, passw)
            return True
        except ldap.INVALID_CREDENTIALS:
            # Bad user/pass
            return False

        # Although we really shouldn't reach here
        return False

    def get_details(self, user, return_list=True):

        # If one username (and a string) is put in a list
        if isinstance(user, str):
            user = [user]

        # Generate the OR list of users to filter by
        joined = ")(uid=".join(user)
        filt = "(|(uid={}))".format(joined)

        basedn = "ou=People,ou=shibboleth,dc=ic,dc=ac,dc=uk"

        query_result = self.conn.search_s(basedn, ldap.SCOPE_SUBTREE, filt)

        output = []

        for dn, entry in query_result:
            # Filter to the values we want to keep
            entry = {key: entry[key] for key in
                                ['uid', 'mail', 'sn', 'givenName', 'displayName']}

            # We want to return strings not a list of one item (results should be one item!)
            for key, item in entry.iteritems():
                entry[key] = item[0]

            # If we are returning a list (default)
            if return_list:
                output.append(entry)
            else:  # This should only be called if ther is one result to return (and as a dict)
                return entry

        return output

    def close(self):
        self.conn.unbind()

    def __del__(self):
        self.close()