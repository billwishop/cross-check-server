"""View module for handling requests about tenants"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from crosscheckapi.models import Tenant, Landlord, TenantPropertyRel
import json
from datetime import date
from datetime import datetime

class Tenants(ViewSet):
    """Cross Check tenants"""

    def create(self, request):
        """Handle POST operations for tenants
        Returns:
            Response -- JSON serialized tenant instance
        """
        landlord = Landlord.objects.get(user=request.auth.user)

        tenant = Tenant()
        tenant.phone_number = request.data["phone_number"]
        tenant.email = request.data["email"]
        tenant.full_name = request.data["full_name"]
        tenant.landlord = landlord
        tenant.rented_property = None

        try:
            tenant.save()
            serializer = TenantSerializer(tenant, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """Handle GET requests for single tenant
        Returns:
            Response -- JSON serialized tenant instance
        """

        try: 
            tenant = Tenant.objects.get(pk=pk)

            try:
                rented_property = TenantPropertyRel.objects.filter(tenant=pk)
                tenant.rented_property = rented_property
            except TenantPropertyRel.DoesNotExist:
                tenant.rented_property = None

            # Check if the lease is active and add a custom property
            current_day = date.today()
            for rp in tenant.rented_property:
                if current_day > rp.lease_start and current_day < rp.lease_end:
                    rp.active = True
                else: 
                    rp.active = False         

            # If the tenant does not have a lease, null will be
            # returned rather than an empty array
            if not tenant.rented_property:
                    tenant.rented_property = None   

            serializer = TenantSerializer(tenant, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """Handle PUT requests for a tenant
        Returns:
            Response -- Empty body with 204 status code
        """
        landlord = Landlord.objects.get(user=request.auth.user)

        tenant = Tenant.objects.get(pk=pk)
        tenant.phone_number = request.data["phone_number"]
        tenant.email = request.data["email"]
        tenant.full_name = request.data["full_name"]
        tenant.landlord = landlord
        tenant.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single tenant
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            tenant = Tenant.objects.get(pk=pk)
            tenant.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Tenant.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to tenants resource
        Returns:
            Response -- JSON serialized list of tenants
        """
        landlord = Landlord.objects.get(user=request.auth.user)
        current_users_tenants = Tenant.objects.filter(landlord=landlord)

        # The table on the front end requires an object where the
        # id's are keys and names are values
        table = self.request.query_params.get('table', None)
        if table is not None:
            tenant_obj = {}
            for tenant in current_users_tenants:
                tenant_obj[tenant.id] = tenant.full_name
            
            to_string = json.dumps(tenant_obj, separators=None)

            return Response(to_string)

        search_term = self.request.query_params.get('search', None)
        if search_term is not None:
            current_users_tenants = current_users_tenants.filter(phone_number__icontains=search_term
                ) | current_users_tenants.filter(email__icontains=search_term
                ) | current_users_tenants.filter(full_name__icontains=search_term
                ) 

        # Connect rented properties to tenants through the relationship table
        try:
            for tenant in current_users_tenants:
                lease = TenantPropertyRel.objects.filter(tenant=tenant)
                tenant.rented_property = lease

                # Check if the lease is active and add a custom property
                current_day = date.today()
                for rp in tenant.rented_property:
                    if current_day > rp.lease_start and current_day < rp.lease_end:
                        rp.active = True
                    else: 
                        rp.active = False

        except TenantPropertyRel.DoesNotExist:
            current_users_tenants.rented_property = None

        # If the tenant does not have a lease, null will be 
        # returned rather than an empty array
        for tenant in current_users_tenants:
            if not tenant.rented_property:
                    tenant.rented_property = None
        
        serializer = TenantSerializer(
            current_users_tenants, many=True, context={'request': request}
        )
        return Response(serializer.data)



class LeaseSerializer(serializers.ModelSerializer):
    """JSON serializer for leases"""
    class Meta:
        model = TenantPropertyRel
        fields = ('id', 'lease_start', 'lease_end', 'rent', 'rented_property', 'active')
        depth = 1

class TenantSerializer(serializers.ModelSerializer):
    """JSON serializer for tenants"""
    rented_property = LeaseSerializer(many=True)
    class Meta:
        model = Tenant
        fields = ('id', 'phone_number', 'email',
                    'landlord', 'full_name', 'rented_property')