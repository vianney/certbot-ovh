# Copyright 2018 Vianney le Clément de Saint-Marcq
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""OVH DNS authenticator plugin"""

import logging

import ovh
import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """OVH DNS authenticator."""

    description = "OVH DNS authenticator"
    ttl = 1

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=10)
        add('credentials', help='OVH credentials config file.')

    def more_info(self):
        return "This plugin configures a DNS TXT record to respond to " \
               "a dns-01 challenge using the OVH API."

    def _setup_credentials(self):
        self._configure_file('credentials', "Credentials config file")

    def _perform(self, domain, validation_name, validation):
        self._get_ovh_client().add_txt_record(domain, validation_name, validation, self.ttl)

    def _cleanup(self, domain, validation_name, validation):
        self._get_ovh_client().del_txt_record(domain, validation_name)

    def _get_ovh_client(self):
        return _OvhClient(self.conf('credentials'))


class _OvhClient(object):
    """
    Encapsulates all communication with the OVH API.
    """

    def __init__(self, conf):
        self.ovh = ovh.Client(config_file=conf)

    def add_txt_record(self, domain, record_name, record_content, record_ttl):
        zone = self._find_zone(domain)
        if not record_name.endswith('.' + zone):
            raise PluginError("Record name {0} is not in DNS zone {1}."
                              .format(record_name, zone))
        subdomain = record_name[:-len(zone)-1]
        record = self._find_record_id(zone, subdomain)
        if record is not None:
            logger.debug("Updating record %d", record)
            try:
                self.ovh.put('/domain/zone/{zone}/record/{record}'
                             .format(zone=zone, record=record),
                             subDomain=subdomain, target=record_content,
                             ttl=record_ttl)
            except ovh.exceptions.APIError as e:
                raise errors.PluginError("Error updating TXT record: {0}"
                                         .format(e))
        else:
            logger.debug("Adding record to zone %s: %s", zone, subdomain)
            try:
                self.ovh.post('/domain/zone/{zone}/record'.format(zone=zone),
                              subDomain=subdomain, fieldType='TXT',
                              target=record_content, ttl=record_ttl)
            except ovh.exceptions.APIError as e:
                raise errors.PluginError("Error creating TXT record: {0}"
                                         .format(e))
        self._refresh_zone(zone)

    def del_txt_record(self, domain, record_name):
        zone = self._find_zone(domain)
        if not record_name.endswith('.' + zone):
            raise PluginError("Record name {0} is not in DNS zone {1}."
                              .format(record_name, zone))
        subdomain = record_name[:-len(zone)-1]
        record = self._find_record_id(zone, subdomain)
        if record is not None:
            try:
                self.ovh.delete('/domain/zone/{zone}/record/{record}'
                                .format(zone=zone, record=record))
            except ovh.exceptions.APIError as e:
                raise errors.PluginError("Error deleting TXT record: {0}"
                                         .format(e))
        self._refresh_zone(zone)

    def _find_zone(self, domain):
        try:
            zones = self.ovh.get('/domain/zone')
        except ovh.exceptions.APIError as e:
            raise errors.PluginError("Error retrieving DNS zones: {0}".format(e))
        for guess in dns_common.base_domain_name_guesses(domain):
            if guess in zones:
                return guess
        raise errors.PluginError("Unable to determine DNS zone for {0}."
                                 "Please confirm that the domain name has been entered correctly "
                                 "and is already associated with the supplied OVH account."
                                 .format(domain))

    def _find_record_id(self, zone, subdomain):
        try:
            records = self.ovh.get('/domain/zone/{zone}/record?fieldType=TXT&subDomain={subdomain}'
                                   .format(zone=zone, subdomain=subdomain))
        except ovh.exceptions.APIError as e:
            raise errors.PluginError("Error querying TXT record of {0} in {1}: {2}"
                                     .format(subdomain, zone, e))
        if len(records) > 0:
            return records[0]
        else:
            return None

    def _refresh_zone(self, zone):
        try:
            self.ovh.post('/domain/zone/{zone}/refresh'.format(zone=zone))
        except ovh.exceptions.APIError as e:
            raise errors.PluginError("Error refreshing DNS zone: {0}"
                                     .format(e))
