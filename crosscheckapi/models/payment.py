from django.db import models

class Payment(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    amount = models.IntegerField()
    ref_num = models.CharField(max_length=100)
    tenant = models.ForeignKey("Tenant", on_delete=models.CASCADE)
    rented_property = models.ForeignKey("Property", on_delete=models.CASCADE, default=None, blank=True, null=True)
    payment_type = models.ForeignKey("PaymentType", on_delete=models.CASCADE)
    landlord = models.ForeignKey("Landlord", on_delete=models.CASCADE)