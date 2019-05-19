"""Models for bitemporal objects."""

from django.db import models
from django.db import transaction
from django.db.models import manager
from django.db.models import query
from django.utils import timezone


class BitemporalQuerySet(query.QuerySet):
    """QuerySet for bitemporal model managers."""

    def valid(self):
        """Return objects that are currently valid."""
        return self.valid_on(timezone.now())

    def valid_on(self, date_time):
        """Return objects that were valid on the given datetime."""
        validity_conditions = (
            models.Q(
                valid_datetime_start__lte=date_time,
                valid_datetime_end__gt=date_time) |
            models.Q(
                valid_datetime_start__lte=date_time,
                valid_datetime_end__isnull=True)
        )
        return self.filter(validity_conditions)

    def supersede(self, values, **kwargs):
        """Supersede the object that matched **kwargs with provided values."""
        lookup, params = self._extract_model_params(values, **kwargs)
        with transaction.atomic(using=self.db):
            # datetime the superseding obj will supersede
            cutoff_datetime = params.get(
                'valid_datetime_start', timezone.now())
            curr_obj = self.select_for_update().valid().get(**lookup)

            # invalidate existing instance
            curr_obj.valid_datetime_end = cutoff_datetime
            curr_obj.save(update_fields=['valid_datetime_end'])

            # create superseding instance
            sup_obj = curr_obj
            sup_obj.pk = None
            sup_obj.valid_datetime_start = cutoff_datetime
            sup_obj.valid_datetime_end = None
            sup_obj.transaction_datetime_start = None
            sup_obj.transaction_datetime_end = None
            for k, v in params.items():
                setattr(sup_obj, k, v() if callable(v) else v)
            sup_obj.save()

        return sup_obj


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
