Change Log
==========

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

1.2.1 (2019-06-10)
------------------

Fixed
~~~~~

* script to update label

Added
~~~~~

* Colissimo adapter to format address in function of the country
  - FRA: default if the adapter does not exist
  - BEL
  - CHE

Refactored
~~~~~~~~~~

* Unittest depend of pytest

1.2.0 (2019-01-16)
------------------

Refactored
~~~~~~~~~~

* ``returned`` status was renamed ``error``, to not create status each time

Fixed
~~~~~

* When a pack have been created for more than 90 days, then the status is now replaced
  by ``error`` status.

1.0.0 (2018-07-07)
------------------

Added
~~~~~

* Delivery Blok
* Colissimo Blok  specialization
