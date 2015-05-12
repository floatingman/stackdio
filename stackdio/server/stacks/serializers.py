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
import os
from datetime import datetime

import salt.cloud

from django.conf import settings
from rest_framework import serializers

from blueprints.models import Blueprint, BlueprintHostDefinition
from blueprints.serializers import (
    BlueprintHostFormulaComponentSerializer,
    BlueprintHostDefinitionSerializer
)
from cloud.serializers import SecurityGroupSerializer
from cloud.models import SecurityGroup
from core.exceptions import BadRequest
from core.utils import recursive_update
from . import models, workflows


logger = logging.getLogger(__name__)


def validate_properties(properties):
    """
    Make sure properties are a valid dict and that they don't contain `__stackdio__`
    """
    if not isinstance(properties, dict):
        raise serializers.ValidationError({
            'properties': ['This field must be a JSON object.']
        })

    if '__stackdio__' in properties:
        raise serializers.ValidationError({
            'properties': ['The `__stackdio__` key is reserved for system use.']
        })


class StackPropertiesSerializer(serializers.Serializer):
    def to_representation(self, obj):
        if obj is not None:
            return obj.properties
        return {}

    def to_internal_value(self, data):
        return data

    def validate(self, attrs):
        validate_properties(attrs)
        return attrs

    def create(self, validated_data):
        """
        We never create anything with this serializer, so just leave it as not implemented
        """
        return super(StackPropertiesSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if self.partial:
            # This is a PATCH, so properly merge in the old data
            old_properties = instance.properties
            instance.properties = recursive_update(old_properties, validated_data)
        else:
            # This is a PUT, so just add the data directly
            instance.properties = validated_data

        # Regenerate the pillar file with the new properties
        instance._generate_pillar_file()

        return instance


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
    owner = serializers.ReadOnlyField(source='owner.username')
    host_count = serializers.ReadOnlyField(source='hosts.count')
    volume_count = serializers.ReadOnlyField(source='volumes.count')
    status = serializers.ReadOnlyField()

    # Identity links
    hosts = serializers.HyperlinkedIdentityField(
        view_name='stack-hosts', read_only=True)
    fqdns = serializers.HyperlinkedIdentityField(
        view_name='stack-fqdns', read_only=True)
    action = serializers.HyperlinkedIdentityField(
        view_name='stack-action', read_only=True)
    actions = serializers.HyperlinkedIdentityField(
        view_name='stackaction-list', read_only=True)
    logs = serializers.HyperlinkedIdentityField(
        view_name='stack-logs', read_only=True)
    orchestration_errors = serializers.HyperlinkedIdentityField(
        view_name='stack-orchestration-errors', read_only=True)
    provisioning_errors = serializers.HyperlinkedIdentityField(
        view_name='stack-provisioning-errors', read_only=True)
    volumes = serializers.HyperlinkedIdentityField(
        view_name='stack-volumes', read_only=True)
    properties = serializers.HyperlinkedIdentityField(
        view_name='stack-properties', read_only=True)
    history = serializers.HyperlinkedIdentityField(
        view_name='stack-history', read_only=True)
    security_groups = serializers.HyperlinkedIdentityField(
        view_name='stack-security-groups', read_only=True)

    # Relation Links
    blueprint = serializers.PrimaryKeyRelatedField(queryset=Blueprint.objects.all())

    class Meta:
        model = models.Stack
        fields = (
            'id',
            'url',
            'blueprint',
            'title',
            'description',
            'status',
            'public',
            'owner',
            'namespace',
            'host_count',
            'volume_count',
            'created',
            'fqdns',
            'hosts',
            'volumes',
            'properties',
            'history',
            'action',
            'actions',
            'security_groups',
            'logs',
            'orchestration_errors',
            'provisioning_errors',
        )

    SECRET_FIELDS = (
        'max_retries',
        'auto_launch',
        'auto_provision',
        'parallel',
        'simulate_launch_failures',
        'simulate_zombies',
        'simulate_ssh_failures',
        'failure_percent',
    )

    REQUIRED_FIELDS = (
        'blueprint',
        'title',
        'description',
        'properties',
    )

    OPTIONAL_FIELDS = (
        'namespace',
        'public',
    )

    VALID_FIELDS = SECRET_FIELDS + REQUIRED_FIELDS + OPTIONAL_FIELDS

    def validate(self, attrs):
        errors = {}

        for k in attrs:
            if k not in self.VALID_FIELDS:
                errors.setdefault('unknown fields', []).append(k)

        if errors:
            raise serializers.ValidationError(errors)

        properties = attrs.get('properties', {})

        # Validate the properties
        validate_properties(properties)

        return attrs

    def create(self, validated_data):
        # Grab all the extra data not in the validated_data

        logger.debug(self.initial_data)

        # OPTIONAL PARAMS
        public = self.initial_data.get('public', False)
        properties = self.initial_data.get('properties', {})
        max_retries = self.initial_data.get('max_retries', 2)

        # UNDOCUMENTED PARAMS
        # Skips launching if set to False
        launch_stack = self.initial_data.get('auto_launch', True)
        provision_stack = self.initial_data.get('auto_provision', True)

        # Launches in parallel mode if set to True
        parallel = self.initial_data.get('parallel', True)

        # See stacks.tasks::launch_hosts for information on these params
        simulate_launch_failures = self.initial_data.get('simulate_launch_failures',
                                                    False)
        simulate_ssh_failures = self.initial_data.get('simulate_ssh_failures',
                                                 False)
        simulate_zombies = self.initial_data.get('simulate_zombies', False)
        failure_percent = self.initial_data.get('failure_percent', 0.3)

        # Grab the validated stuff
        title = validated_data['title']
        description = validated_data['description']
        blueprint = validated_data['blueprint']
        user = validated_data['owner']

        # Generate the title and/or description if not provided by user
        if not title and not description:
            extra_description = ' (Title and description'
        elif not title:
            extra_description = ' (Title'
        elif not description:
            extra_description = ' (Description'
        else:
            extra_description = ''
        if extra_description:
            extra_description += ' auto generated from Blueprint {0})'.format(blueprint.pk)

        if not title:
            validated_data['title'] = '{0} ({1})'.format(
                blueprint.title,
                datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            )

        if not description:
            description = blueprint.description
        validated_data['description'] = description + extra_description

        # check for duplicates
        if models.Stack.objects.filter(owner=user,
                                       title=title).count():
            raise serializers.ValidationError({
                'title': ['A Stack with this title already exists in your account.']
            })

        # check for hostname collisions if namespace is provided
        namespace = validated_data.get('namespace')

        host_definitions = blueprint.host_definitions.all()
        hostnames = models.get_hostnames_from_hostdefs(
            host_definitions,
            username=user.username,
            namespace=namespace
        )

        if namespace:
            # If the namespace was not provided, then there is no chance
            # of collision within the database

            # query for existing host names
            # Leave this in so that we catch errors faster if they are local,
            #    Only hit up salt cloud if there are no duplicates locally
            hosts = models.Host.objects.filter(hostname__in=hostnames)
            if hosts.count():
                raise serializers.ValidationError({
                    'duplicate_hostnames': [h.hostname for h in hosts]
                })

        salt_cloud = salt.cloud.CloudClient(os.path.join(
            settings.STACKDIO_CONFIG.salt_config_root,
            'cloud'
        ))
        query = salt_cloud.query()

        # Since a blueprint can have multiple providers
        providers = set()
        for bhd in host_definitions:
            providers.add(bhd.cloud_profile.cloud_provider)

        # Check to find duplicates
        dups = []
        for provider in providers:
            provider_type = provider.provider_type.type_name
            for instance, details in query.get(provider.slug, {}).get(provider_type, {}).items():
                if instance in hostnames:
                    if details['state'] not in ('shutting-down', 'terminated'):
                        dups.append(instance)

        if dups:
            raise serializers.ValidationError({
                'duplicate_hostnames': dups
            })

        # Everything is valid!  Let's create the stack in the database
        try:
            stack = models.Stack.objects.create_stack(
                user,
                blueprint,
                title=title,
                description=description,
                namespace=namespace,
                public=public,
                properties=properties
            )
        except Exception, e:
            raise BadRequest(str(e))

        # The stack was created, now let's launch it
        if launch_stack:
            workflow = workflows.LaunchWorkflow(stack)
            workflow.opts.provision = provision_stack
            workflow.opts.parallel = parallel
            workflow.opts.max_retries = max_retries
            workflow.opts.simulate_launch_failures = simulate_launch_failures
            workflow.opts.simulate_ssh_failures = simulate_ssh_failures
            workflow.opts.simulate_zombies = simulate_zombies
            workflow.opts.failure_percent = failure_percent
            workflow.execute()

            stack.set_status('queued', models.Stack.PENDING,
                             'Stack has been submitted to launch queue.')

        return stack


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
