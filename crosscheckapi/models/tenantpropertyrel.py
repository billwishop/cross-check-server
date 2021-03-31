from django.db import models

class TenantPropertyRel(models.Model):
    lease_start = models.DateField(auto_now=False, auto_now_add=False)
    lease_end = models.DateField(auto_now=False, auto_now_add=False)
    rent = models.IntegerField()
    tenant = models.ForeignKey("Tenant", on_delete=models.CASCADE)
    rented_property = models.ForeignKey("Property", on_delete=models.CASCADE)

    @property
    def active(self):
        return self.__active

    @active.setter
    def active(self, value):
        self.__active = value