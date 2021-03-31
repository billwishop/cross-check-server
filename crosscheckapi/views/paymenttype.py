"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from crosscheckapi.models import PaymentType
import json

class PaymentTypes(ViewSet):
    """ Cross Check PaymentTypes """

    def list(self, request):
        """Handle GET requests to payment_type resource
        Returns:
            Response -- JSON serialized list of payment_types
        """
        payment_types = PaymentType.objects.all()

        # The table on the front end requires a specific data structure
        # {id: label, id: label, etc.}
        pt_obj = {}
        for pt in payment_types:
            pt_obj[pt.id] = pt.label

        pt_obj_string = json.dumps(pt_obj, separators=None)

        return Response(pt_obj_string)

class PaymentTypeSerializer(serializers.ModelSerializer):
    """JSON serializer for payment_types"""
    class Meta:
        model = PaymentType
        fields = ('id', 'label')