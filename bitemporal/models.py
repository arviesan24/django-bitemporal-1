"""Models for bitemporal objects."""

from django.db import models
from django.db.models import manager
from django.db.models import query


class BitemporalQuerySet(query.QuerySet):
    """QuerySet for bitemporal model managers."""

    def valid(self):
        """Return objects that are currently valid."""
        return self.filter(valid_datetime_end__isnull=True)

    def valid_on(self, date_time):
        """Return objects that were valid on the given datetime."""
        condition = (
            models.Q(
                valid_datetime_start__lte=date_time,
                valid_datetime_end__gt=date_time) |
            models.Q(
                valid_datetime_start__lte=date_time,
                valid_datetime_end__isnull=True)
        )
        return self.filter(condition)


class BitemporalManager(manager.BaseManager.from_queryset(BitemporalQuerySet)):
    """Model manager for bitemporal models."""

    use_in_migrations = True


class BitemporalModel(models.Model):
    """Base model class for bitemporal models."""

    valid_datetime_start = models.DateTimeField(db_index=True)
    valid_datetime_end = models.DateTimeField(
        blank=True, null=True, db_index=True)
    transaction_datetime_start = models.DateTimeField(
        auto_now_add=True, db_index=True)
    transaction_datetime_end = models.DateTimeField(
        blank=True, null=True, db_index=True)

    objects = BitemporalManager()

    class Meta:
        """Model options for `BitemporalModel`."""

        abstract = True
