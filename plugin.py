###
# Copyright (c) 2012, Andrew Smillie
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import time as epoch
import os, sys, ldap


class GeekSoc(callbacks.Plugin):
    """Add the help for "@plugin help GeekSoc" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    def __init__(self, irc):
        super(GeekSoc, self).__init__(irc)
    
    def userinfo(self, irc, msg, args, name):
        """<username>
         
         Return information on a given username.
        """
        user = name
        day = int(epoch.time()/(60*60*24))
        
        try:
            l = ldap.open("ldap.geeksoc.org")
            l.protocol_version = ldap.VERSION3
        except ldap.LDAPError, e:
            irc.reply('Error getting info for user: "%s"' % name)
            return
        
        baseDN = "ou=People, dc=geeksoc, dc=org"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "uid={0}".format(user)
        
        try:
            results = l.search_s(baseDN, searchScope, searchFilter, retrieveAttributes)
            if (len(results) == 0):
                irc.reply('User "%s" doesn\'t exist' % name)
                return
    
            for dn, entry in results:
                name = entry['cn'][0]
                email = entry['mail'][0]
                studentNo = entry['studentNumber'][0] if 'studentNumber' in entry else "N/A"
                expiry = entry['shadowExpire'][0] if 'shadowExpire' in entry else "999999"
                paid = entry['hasPaid'][0] if 'hasPaid' in entry else "N/A"
                
                status = "Active"
                if (paid == "FALSE"):
                    status = "Active (Not Paid)"
                if int(expiry) <= day+60:
                    status = "Expiring (in %s days)" % (int(expiry)-day)
                if int(expiry) <= day:
                    status = "Expired (%s days ago)" % (day-int(expiry))
                if int(expiry) == 1:
                    status = "Admin disabled"
                
                string = ( "User: %s, Name: %s, Email: %s, Student Number: %s, Status: %s" % (user, name, email, studentNo, status) )
                irc.reply(string.encode('utf-8'))
            
            baseDN = "ou=Groups, dc=geeksoc, dc=org"
            searchFilter = "(memberUid=*)"
            results = l.search_s(baseDN, ldap.SCOPE_SUBTREE, searchFilter)
            groups = ''
            for dn, entry in results:
                if user in entry['memberUid']:
                    groups += entry['cn'][0] + ' '
            irc.reply("Groups: " + groups)
        
        except ldap.LDAPError, e:
            irc.reply(e)

    userinfo = wrap(userinfo, ['text'])


    def group(self, irc, msg, args, name):
        """<group>
         
         Return information on a given group.
        """
        group = name
        
        try:
            l = ldap.open("ldap.geeksoc.org")
            l.protocol_version = ldap.VERSION3
        except ldap.LDAPError, e:
            irc.reply('Error getting info for user: "%s"' % name)
            return
        
        baseDN = "cn=%s,ou=Groups, dc=geeksoc, dc=org" %(group)
        searchFilter = "(memberUid=*)"
        
        try:
            results = l.search_s(baseDN, ldap.SCOPE_SUBTREE, searchFilter)
            string = ''
            for dn, entry in results:
                for u in entry['memberUid']:
                    string += u + ' '
            irc.reply("Group: %s, Members: %s" % (group, string))

        except ldap.LDAPError, e:
            irc.reply(e)

    group = wrap(group, ['text'])


Class = GeekSoc


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
