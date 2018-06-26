# This file is a part of the AnyBlok project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import anyblok
from anyblok.release import version
from anyblok.config import Configuration

Configuration.add_application_properties(
    'update_labels_status',
    [
        'logging',
        'dramatiq-broker',
    ],
    prog='AnyBlok update label status, version %r' % version,
    description="Update label status"
)


def update_labels_status():
    """Execute a script or open an interpreter
    """
    registry = anyblok.start('update_labels_status')
    if registry:
        registry.Delivery.Shipment.get_labels_status()
