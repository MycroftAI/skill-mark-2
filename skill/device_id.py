# Copyright 2021 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mycroft.api import _get_pantacor_device_id
from mycroft.identity import IdentityManager


def get_mycroft_uuid():
    """Get the UUID of a Mycroft device paired with the Mycroft backend."""
    identity = IdentityManager.get()
    return identity.uuid

def get_pantacor_device_id():
    """Get the Pantacor device-id for devices using the Pantacor update system."""
    # TODO this uses the temporary solution in the feature/mark-2 branch.
    # It should be replaced when a better solution is available.
    return _get_pantacor_device_id()


