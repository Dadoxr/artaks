from django.db import models

class Contact(models.Model):

    abc = models.IntegerField()
    start = models.IntegerField()
    end = models.IntegerField()
    operator = models.CharField()
    region = models.CharField()
    territory = models.CharField()
    inn = models.BigIntegerField()

    def __str__(self):
        return f'{self.pk}, {self.abc}, {self.start}, {self.end}, {self.inn}'
    

    class Meta:
        verbose_name = 'contact'
        verbose_name_plural = 'contacts'