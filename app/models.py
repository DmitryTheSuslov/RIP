from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


MONTHS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    address_name = models.CharField(max_length=100, verbose_name="Адрес", default="address")
    area = models.IntegerField(default=0, verbose_name='Площадь')
    photo = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, default='active')

    def __str__(self):
        return self.address_name
    
    def get_counter_value(self, fix):
        mm = AddressFixation.objects.filter(address=self, fixation=fix).first()
        return mm.water_counter_value if mm else None

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
        db_table = "addresses"
        managed = True

class Fixation(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален'),
    )
    fixation_id = models.AutoField(primary_key=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    month = models.IntegerField(null=True, verbose_name="Месяц")
    created_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True, related_name='moderator')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1,blank=True, null=True)

    def __str__(self):
        return "Фиксация №" + str(self.pk)

    class Meta:
        verbose_name = "Фиксация"
        verbose_name_plural = "Фиксации"
        ordering = ('-submitted_at', )
        db_table = "fixations"

    def GetAddresses(self):
        return AddressFixation.objects.filter(fixation=self).values_list('address', flat=True)

class AddressFixation(models.Model):
    mm_id = models.AutoField(primary_key=True)
    address = models.ForeignKey(Address, models.DO_NOTHING, blank=True, null=True)
    fixation = models.ForeignKey(Fixation, models.DO_NOTHING, blank=True, null=True)
    water_counter_value = models.IntegerField(verbose_name="Поле м-м", blank=True, null=True)
    pay_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "address_fixation"
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['address', 'fixation'], name='unique_AddressFixation')
        ]
