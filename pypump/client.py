##
#   Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
#   This program is free software: you can redistribute it and/or modify 
#   it under the terms of the GNU General Public License as published by 
#   the Free Software Foundation, either version 3 of the License, or 
#   (at your option) any later version. 
# 
#   This program is distributed in the hope that it will be useful, 
#   but WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
#   GNU General Public License for more details. 
# 
#   You should have received a copy of the GNU General Public License 
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from __future__ import absolute_import

import json
import logging

import requests

_log = logging.getLogger(__name__)

class ClientException(Exception):
    
    def __init__(self, message, context=None, *args, **kwargs):
        if context is not None:
            message = "{0} (context: {1})".format(message, context)
        
        super(ClientException, self).__init__(message, *args, **kwargs)

class Client(object):

    ENDPOINT = "api/client/register"

    _pump = None

    webfinger = None
    request = None
    logo = None
    contacts = None
    redirect = None
    type = None

    key = None
    secret = None
    expirey = 0 # never


    def __init__(self, webfinger, type, name=None, contacts=None, redirect=None, 
                 logo=None, key=None, secret=None, expirey=None):

        self.webfinger = webfinger
        self.name = name 
        self.type = type
        self.logo = logo
        self.contacts = contacts or []
        self.redirect = redirect or []

        self.key = key or self.key
        self.secret = secret or self.secret
        self.expirey = expirey or self.expirey

    @property
    def server(self):
        return self.webfinger.split("@", 1)[1]
    
    @property
    def nickname(self):
        return self.webfinger.split("@", 1)[0]

    def set_pump(self, pump):
        self._pump = pump

    @property
    def context(self):
        """ Provides request context """
        type = "client_associate" if self.key is None else "client_update"
        data = {
            "type": type, 
            "application_type": self.type,
        }

        # is this an update?
        if self.key:
            data["client_id"] = self.key
            data["client_secret"] = self.secret

        # Add optional params
        if self.name:
            data["application_name"] = self.name

        if self.logo:
            data["logo_url"] = self.logo

        if self.contacts:
            # space seporated list
            data["contacts"] = " ".join(self.contacts)

        if self.redirect:
            data["redirect_uri"] = " ".join(self.redirect)

        # Convert to JSON  and send
        return json.dumps(data)

    def request(self, server=None):
        """ Sends the request """
        request = {
                "headers": {"Content-Type": "application/json"},
                "data": self.context,
                }
        
        url = "{proto}://{server}/{endpoint}".format(
            proto=self._pump.protocol,
            server = server or self.server,
            endpoint = self.ENDPOINT
        )
        
        response = self._pump._requester(requests.post, url, **request)
        
        try:
            server_data = response.json()
        except ValueError:
            raise ClientException(response.content)

        if "error" in server_data:
            raise ClientException(server_data["error"], self.context)

        _log.debug("Client registration recieved: %(id)s %(secret)s %(expire)s", {
                "id": server_data["client_id"],
                "secret": server_data["client_secret"],
                "expire": server_data["expires_at"]
                })
        
        return server_data

    def register(self, server=None):
        """ Sends a client registration request """
        if (self.key or self.secret):
            return self.update()
 
        server_data = self.request(server)

        self.key = server_data["client_id"]
        self.secret = server_data["client_secret"]
        self.expirey = server_data["expires_at"]

    def update(self):
        """ Updates a previously registerd client """
        error = ""

        if self.key is None:
            error = "To update a client you need to provide a key"
        if self.secret is None:
            error = "To update a client you need to provide the secret"

        if error:
            raise ClientException(error)

        self.request()
        return True

    def __repr__(self):
        if self.key:
            return "<Client {0} ({1})>".format(self.server, self.key)
        return "<Client {0}>".format(self.server)

    def __str__(self):
        return repr(self)

