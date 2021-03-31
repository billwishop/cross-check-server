from django.db import models

class Property(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    landlord = models.ForeignKey("Landlord", on_delete=models.CASCADE)

    @property
    def lease(self):
        return self.__lease

    @lease.setter
    def lease(self, value):
        self.__lease = value