"""View module for handling requests about properties"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from datetime import date
from datetime import datetime
from crosscheckapi.models import Property, Tenant, Landlord, Payment, PaymentType, TenantPropertyRel


class Properties(ViewSet):
    """Cross Check Properties"""

    def create(self, request):
        """Handle POST operations for properties
        Returns:
            Response -- JSON serialized property instance
        """
        # landlord = authenticated user
        landlord = Landlord.objects.get(user=request.auth.user)

        rental = Property()
        rental.street = request.data["street"]
        rental.city = request.data["city"]
        rental.state = request.data["state"]
        rental.postal_code = request.data["postal_code"]
        rental.landlord = landlord

        rental.save()

        serializer = PropertySerializer(
            rental, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single property
        Returns:
            Response -- JSON serialized property instance
        """
        try:
            rental = Property.objects.get(pk=pk)

            # Find the associated leases and attach them to the custom property `lease`
            try:
                leases = TenantPropertyRel.objects.filter(rented_property=pk)

                # Set the custom property `active` based on the lease date range
                current_day = date.today()
                for lease in leases:
                    if current_day >= lease.lease_start and current_day <= lease.lease_end:
                        lease.active = True
                    else: 
                        lease.active = False
                rental.lease = leases

            except TenantPropertyRel.DoesNotExist:
                rental.lease = None

            serializer = LeasedPropertySerializer(
                rental, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to property resource
        Returns:
            Response -- JSON serialized list of properties
        """
        landlord = Landlord.objects.get(user=request.auth.user)
        current_users_properties = Property.objects.filter(landlord=landlord)

        search_term = self.request.query_params.get('search', None)
        if search_term is not None:
            current_users_properties = current_users_properties.filter(street__icontains=search_term
            ) | current_users_properties.filter(city__icontains=search_term
            ) | current_users_properties.filter(state__icontains=search_term
            ) | current_users_properties.filter(postal_code__icontains=search_term
            )

        serializer = PropertySerializer(
            current_users_properties, many=True, context={'request': request})

        return Response(serializer.data)

    def update(self, request, pk=None):
        """Handle PUT requests for properties
        Returns:
            Response -- Empty body with 204 status code
        """
        # landlord = authenticated user
        landlord = Landlord.objects.get(user=request.auth.user)

        rental = Property.objects.get(pk=pk)
        rental.street = request.data["street"]
        rental.city = request.data["city"]
        rental.state = request.data["state"]
        rental.postal_code = request.data["postal_code"]
        rental.landlord = landlord

        rental.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for properties
        Returns:
            Response -- 204, 404, or 500 status code
        """
        try:
            rental = Property.objects.get(pk=pk)
            rental.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Property.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post', 'delete'], detail=True)
    def lease(self, request, pk=None):
        """Managing leases between properties and tenants"""

        # A landlord is creating a lease 
        if request.method == "POST":
            tenant = Tenant.objects.get(pk=request.data["tenant"])
            rented_property = Property.objects.get(pk=pk)

            lease = TenantPropertyRel()
            lease.lease_start = request.data["lease_start"]
            lease.lease_end = request.data["lease_end"]
            lease.rent = request.data["rent"]
            lease.tenant = tenant
            lease.rented_property = rented_property
            lease.save()

            return Response({}, status=status.HTTP_201_CREATED)

        # Delete lease
        elif request.method == "DELETE":
            lease = TenantPropertyRel.objects.get(pk = request.data["lease_id"])
            lease.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)


class LeaseSerializer(serializers.ModelSerializer):
    """JSON serializer for leases"""
    class Meta:
        model = TenantPropertyRel
        fields = ('id', 'lease_start', 'lease_end', 'rent', 'tenant', 'active')
        depth = 2

class LeasedPropertySerializer(serializers.ModelSerializer):
    """JSON serializer for individual properties with the associated leases"""
    lease = LeaseSerializer(many=True)
    class Meta:
        model = Property
        fields = ('id', 'street', 'city', 
        'state', 'postal_code', 'landlord', 'lease')

class PropertySerializer(serializers.ModelSerializer):
    """JSON serializer for properties"""
    class Meta:
        model = Property
        fields = ('id', 'street', 'city', 
        'state', 'postal_code', 'landlord')