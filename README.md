OVH DNS authenticator for certbot
==================================


Installation
-------------

    python setup.py install


Usage
------

Create a configuration file by following the instruction at
<https://github.com/ovh/python-ovh>.
This plugin needs full recursive read/write access on `/domain/zone`.

To request a certificate, use:

    certbot certonly -a certbot-ovh:dns -d mydomain.example.com


License
--------

Copyright 2018 Vianney le Clément de Saint-Marcq

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
<http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
