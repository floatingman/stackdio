# -*- coding: utf-8 -*-

# Copyright 2014,  Digital Reasoning
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import logging

from rest_framework import serializers

from blueprints.models import BlueprintHostDefinition
from blueprints.serializers import (
    BlueprintHostFormulaComponentSerializer,
    BlueprintHostDefinitionSerializer
)
from cloud.serializers import SecurityGroupSerializer
from cloud.models import SecurityGroup
from core.utils import recursive_update
from . import models

logger = logging.getLogger(__name__)


class StackPropertiesSerializer(serializers.Serializer):
    def to_representation(self, obj):
        if obj is not None:
            return obj.properties
        return {}

    def to_internal_value(self, data):
        return data

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        return recursive_update(instance, validated_data)


class HostSerializer(serializers.HyperlinkedModelSerializer):
    # Read only fields
    subnet_id = serializers.ReadOnlyField()
    availability_zone = serializers.PrimaryKeyRelatedField(read_only=True)
    formula_components = BlueprintHostFormulaComponentSerializer(many=True, read_only=True)

    class Meta:
        model = models.Host
        fields = (
            'id',
            'url',
            'hostname',
            'provider_dns',
            'provider_private_dns',
            'provider_private_ip',
            'fqdn',
            'state',
            'state_reason',
            'status',
            'status_detail',
            'availability_zone',
            'subnet_id',
            'created',
            'sir_id',
            'sir_price',
            'formula_components',
        )


class StackHistorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.StackHistory
        fields = (
            'event',
            'status',
            'status_detail',
            'level',
            'created'
        )


class StackSerializer(serializers.HyperlinkedModelSerializer):
    # Read only fields
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    host_count = serializers.ReadOnlyField(source='hosts.count')
    volume_count = serializers.ReadOnlyField(source='volumes.count')
    status = serializers.ReadOnlyField()

    # Identity links
    hosts = serializers.HyperlinkedIdentityField(
        view_name='stack-hosts')
    fqdns = serializers.HyperlinkedIdentityField(
        view_name='stack-fqdns')
    action = serializers.HyperlinkedIdentityField(
        view_name='stack-action')
    actions = serializers.HyperlinkedIdentityField(
        view_name='stackaction-list')
    logs = serializers.HyperlinkedIdentityField(
        view_name='stack-logs')
    orchestration_errors = serializers.HyperlinkedIdentityField(
        view_name='stack-orchestration-errors')
    provisioning_errors = serializers.HyperlinkedIdentityField(
        view_name='stack-provisioning-errors')
    volumes = serializers.HyperlinkedIdentityField(
        view_name='stack-volumes')
    properties = serializers.HyperlinkedIdentityField(
        view_name='stack-properties')
    history = serializers.HyperlinkedIdentityField(
        view_name='stack-history')
    # access_rules = serializers.HyperlinkedIdentityField(
    #     view_name='stack-access-rules')
    security_groups = serializers.HyperlinkedIdentityField(
        view_name='stack-security-groups')

    class Meta:
        model = models.Stack
        fields = (
            'id',
            'title',
            'description',
            'status',
            'public',
            'url',
            'owner',
            'namespace',
            'host_count',
            'volume_count',
            'created',
            'blueprint',
            'fqdns',
            'hosts',
            'volumes',
            'properties',
            'history',
            'action',
            'actions',
            # 'access_rules',
            'security_groups',
            'logs',
            'orchestration_errors',
            'provisioning_errors',
        )


class StackBlueprintHostDefinitionSerializer(BlueprintHostDefinitionSerializer):
    class Meta:
        model = BlueprintHostDefinition
        fields = (
            'title',
            'description',
        )


class StackSecurityGroupSerializer(SecurityGroupSerializer):
    blueprint_host_definition = StackBlueprintHostDefinitionSerializer()

    class Meta:
        model = SecurityGroup
        fields = (
            'id',
            'url',
            'name',
            'description',
            'rules_url',
            'group_id',
            'blueprint_host_definition',
            'cloud_provider',
            'provider_id',
            'owner',
            'is_default',
            'is_managed',
            'active_hosts',
            'rules',
        )


class StackActionSerializer(serializers.HyperlinkedModelSerializer):
    zip_url = serializers.HyperlinkedIdentityField(view_name='stackaction-zip')

    class Meta:
        model = models.StackAction
        fields = (
            'id',
            'url',
            'zip_url',
            'submit_time',
            'start_time',
            'finish_time',
            'status',
            'type',
            'host_target',
            'command',
            'std_out',
            'std_err',
        )
