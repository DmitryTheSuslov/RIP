from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

from bmstu_lab.utils import STATUS_CHOICES


MONTHS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class Address(models.Model):
    address = models.CharField(max_length=100, verbose_name="Адрес")
    area = models.IntegerField(default=0, verbose_name='Площадь')
    image = models.CharField(default="images/default.png")

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
        db_table = "addresses"


class Fixation(models.Model):
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)
    month = models.IntegerField(default=0, verbose_name="Месяц")

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True, related_name='moderator')

    def __str__(self):
        return "Фиксация №" + str(self.pk)

    def get_addresses(self):
        res = []

        for item in AddressFixation.objects.filter(fixation=self):
            tmp = item.address
            tmp.value = item.value
            res.append(tmp)

        return res

    def get_status(self):
        return dict(STATUS_CHOICES).get(self.status)

    class Meta:
        verbose_name = "Фиксация"
        verbose_name_plural = "Фиксации"
        ordering = ('-date_formation', )
        db_table = "fixations"


class AddressFixation(models.Model):
    address = models.ForeignKey(Address, models.CASCADE)
    fixation = models.ForeignKey(Fixation, models.CASCADE)
    value = models.IntegerField(verbose_name="Поле м-м", blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "address_fixation"