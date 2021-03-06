#!/usr/bin/env python3
# coding=utf-8
import logging
from requests_oauthlib import OAuth1Session
from json import dumps

from six.moves.urllib.parse import urlencode


log = logging.getLogger()


class RestAPIClient(object):
    default_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = None

    def __init__(self,
                 url,
                 consumer_key,
                 consumer_secret,
                 access_token,
                 access_token_secret,
                 advanced_mode,
                 verify_ssl=None,
                 proxies=None,
                 timeout=None,
                 ):
        self._url = url
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._proxies = proxies
        self._advanced_mode = advanced_mode
        self._session = OAuth1Session(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)


    def __exit__(self, *_):
        self.close()

    @staticmethod
    def _response_handler(response):
        try:
            return response.json()
        except ValueError:
            log.debug('Received response with no content')
            return None
        except Exception as e:
            log.error(e)
            return None

    @staticmethod
    def url_joiner(url, path, trailing=None):
        url_link = path
        if url:
            url_link = '/'.join(s.strip('/') for s in [url, path])
        if trailing:
            url_link += '/'
        return url_link


    def close(self):
        return self._session.close()

    def request(self, method='GET', path='/', data=None, json=None, flags=None, params=None, headers=None,
                files=None, trailing=None):
        """

        :param method:
        :param path:
        :param data:
        :param json:
        :param flags:
        :param params:
        :param headers:
        :param files:
        :param trailing: bool
        :return:
        """
        url = self.url_joiner(self._url, path, trailing)
        if params or flags:
            url += '?'
        if params:
            url += urlencode(params or {})
        if flags:
            url += ('&' if params else '') + '&'.join(flags or [])
        json_dump = None
        if files is None:
            data = None if not data else dumps(data)
            json_dump = None if not json else dumps(json)

        headers = headers or self.default_headers
        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            json=json,
            timeout=self._timeout,
            verify=self._verify_ssl,
            files=files,
            proxies=self._proxies
        )

        response.encoding = 'utf-8'

        if self._advanced_mode:
            return response

        log.debug(f"HTTP: {method} {path} -> {response.status_code} {response.reason}")
        response.raise_for_status()
        return response

    def get(self, path, data=None, flags=None, params=None, headers=None, not_json_response=None, trailing=None):
        """
        Get request based on the python-requests module. You can override headers, and also, get not json response
        :param path:
        :param data:
        :param flags:
        :param params:
        :param headers:
        :param not_json_response: OPTIONAL: For get content from raw requests packet
        :param trailing: OPTIONAL: for wrap slash symbol in the end of string
        :return:
        """

        response = self.request('GET', path=path, flags=flags, params=params, data=data, headers=headers,
                                trailing=trailing)
        if self._advanced_mode:
            return response
        if not_json_response:
            return response.content
        else:
            if not response.text:
                return None
            try:
                return response.json()
            except Exception as e:
                log.error(e)
                return response.text

    def post(self, path, data=None, json=None, headers=None, files=None, params=None, trailing=None):
        response = self.request('POST', path=path, data=data, json=json, headers=headers, files=files, params=params,
                                trailing=trailing)
        if self._advanced_mode:
            return response
        return self._response_handler(response)

    def put(self, path, data=None, headers=None, files=None, trailing=None, params=None):
        response = self.request('PUT', path=path, data=data, headers=headers, files=files, params=params,
                                trailing=trailing)

        if self._advanced_mode:
            return response
        return self._response_handler(response)

    def delete(self, path, data=None, headers=None, params=None, trailing=None):
        """
        Deletes resources at given paths.
        :rtype: dict
        :return: Empty dictionary to have consistent interface.
        """
        response = self.request('DELETE', path=path, data=data, headers=headers, params=params, trailing=trailing)
        if self._advanced_mode:
            return response
        return self._response_handler(response)
