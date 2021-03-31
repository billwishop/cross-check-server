from django.db import models

class Tenant(models.Model):
    phone_number = models.CharField(max_length=15, default=None, blank=True, null=True)
    email = models.CharField(max_length=150, default=None, blank=True, null=True)
    full_name = models.CharField(max_length=150)
    landlord = models.ForeignKey("Landlord", on_delete=models.CASCADE)

    @property
    def rented_property(self):
        return self.__rented_property

    @rented_property.setter
    def rented_property(self, value):
        self.__rented_property = value