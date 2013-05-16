# Copyright (c) 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from stevedore import named

from barbican.common.exception import BarbicanException
from barbican.openstack.common.gettextutils import _


class CryptoMimeTypeNotSupportedException(BarbicanException):
    """Raised when support for requested mime type is
    not available in any active plugin."""
    def __init__(self, mime_type):
        super(CryptoMimeTypeNotSupportedException, self).__init__(
            _("Crypto Mime Type of '{0}' not supported").format(mime_type)
        )
        self.mime_type = mime_type


class CryptoAcceptNotSupportedException(BarbicanException):
    """Raised when requested decripted format is not
    available in any active plugin."""
    def __init__(self, accept):
        super(CryptoAcceptNotSupportedException, self).__init__(
            _("Crypto Accept of '{0}' not supported").format(accept)
        )
        self.accept = accept


class CryptoNoSecretOrDataException(BarbicanException):
    """Raised when secret information is not available for the specified
    secret mime-type."""
    def __init__(self, mime_type):
        super(CryptoNoSecretOrDataException, self).__init__(
            _('No secret information available for '
              'Mime Type of {0}').format(mime_type)
        )
        self.mime_type = mime_type


class CryptoExtensionManager(named.NamedExtensionManager):
    def __init__(self, namespace, names,
                 invoke_on_load=True, invoke_args=(), invoke_kwargs={}):
        super(CryptoExtensionManager, self).__init__(
            namespace,
            names,
            invoke_on_load=invoke_on_load,
            invoke_args=invoke_args,
            invoke_kwds=invoke_kwargs
        )

    def encrypt(self, unencrypted, secret, tenant):
        """Delegates encryption to active plugins."""
        for ext in self.extensions:
            if ext.obj.supports(secret.mime_type):
                return ext.obj.encrypt(unencrypted, secret, tenant)
        else:
            raise CryptoMimeTypeNotSupportedException(secret.mime_type)

    def decrypt(self, accept, secret, tenant):
        """Delegates decryption to active plugins."""
        if not secret or not secret.encrypted_data:
            raise CryptoNoSecretOrDataException(accept)

        plain_text = None
        for ext in self.extensions:
            if ext.obj.supports(accept):
                plain_text = ext.obj.decrypt(accept, secret, tenant)
                break
        else:
            raise CryptoAcceptNotSupportedException(accept)

        if not plain_text:
            raise CryptoNoSecretOrDataException(accept)

        return plain_text
