"""Exception classes related to bitemporal objects."""


class BitemporalObjectAlreadySuperseded(Exception):
    """Exception raised when bitemporal object is already superseded."""

    def __init__(self, obj):
        """Initialize exception with the already superseded object."""
        super().__init__(
            'Bitemporal object {} is already superseded and can no '
            'longer be superseded.'.format(obj))
