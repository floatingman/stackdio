define(["knockout"], function (ko) {
    return {
        SecurityGroupRules : ko.observableArray([]),
        DefaultSecurityGroups : ko.observableArray([]),
        SecurityGroups : ko.observableArray([]),
        Zones : ko.observableArray([]),
        ProviderTypes : ko.observableArray([]),
        Accounts : ko.observableArray([]),
        Profiles : ko.observableArray([]),
        NewHosts : ko.observableArray([]),
        HostVolumes : ko.observableArray([]),
        InstanceSizes : ko.observableArray([]),
        Roles : ko.observableArray([]),
        Snapshots : ko.observableArray([]),
        HostMetadata : ko.observableArray([]),
        Stacks : ko.observableArray([]),
        StackHosts : ko.observableArray([])
    }
});
