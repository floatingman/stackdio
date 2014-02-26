define([
    'q', 
    'knockout',
    'viewmodel/base',
    'util/postOffice',
    'util/form',
    'store/Blueprints',
    'store/HostAccessRules',
    'store/BlueprintHosts',
    'api/api',
    'model/models'
],
function (Q, ko, base, _O_, formutils, BlueprintStore, HostRuleStore, BlueprintHostStore, API, models) {
    var vm = function () {
        var self = this;

        /*
         *  ==================================================================================
         *   V I E W   V A R I A B L E S
         *  ==================================================================================
        */
        self.selectedBlueprint = ko.observable();
        self.blueprintTitle = ko.observable();
        self.selectedHost = ko.observable();
        self.hostTitle = ko.observable();

        self.BlueprintStore = BlueprintStore;
        self.HostRuleStore = HostRuleStore;
        self.BlueprintHostStore = BlueprintHostStore;

        /*
         *  ==================================================================================
         *   R E G I S T R A T I O N   S E C T I O N
         *  ==================================================================================
        */
        self.id = 'accessrule.detail';
        self.templatePath = 'accessrule.html';
        self.domBindingId = '#accessrule-detail';

        try {
            self.$66.register(self);
        } catch (ex) {
            console.log(ex);            
        }


        /*
         *  ==================================================================================
         *   E V E N T   S U B S C R I P T I O N S
         *  ==================================================================================
         */
        _O_.subscribe('accessrule.detail.rendered', function (data) {
            self.init(data);
        });


        /*
         *  ==================================================================================
         *   V I E W   M E T H O D S
         *  ==================================================================================
         */

        self.init = function (data) {
            var blueprint = null;
            var host = null;


            if (data.hasOwnProperty('blueprint')) {
                blueprint = BlueprintStore.collection().filter(function (p) {
                    return p.id === parseInt(data.blueprint, 10)
                })[0];

                self.blueprintTitle(blueprint.title);
            } else {
                self.blueprintTitle('New Blueprint');
            }
            self.selectedBlueprint(blueprint);


            if (data.hasOwnProperty('host')) {
                host = BlueprintHostStore.collection().filter(function (h) {
                    return h.id === parseInt(data.host, 10)
                })[0];

                self.hostTitle(host.title);
            } else {
                self.hostTitle('New Host');
            }
            self.selectedHost(host);

        };

        self.addRule = function (model, evt) {
            var record = formutils.collectFormFields(evt.target.form);
            console.log(record);
            var rule;

            if (record.rule_ip_address.value !== '') {
                rule = record.rule_ip_address.value;
            } else if (record.rule_group.value !== '') {
                rule = record.rule_group.value;
            }

            var accessRule = {
                protocol: record.rule_protocol.value,
                from_port: record.rule_from_port.value,
                to_port: record.rule_to_port.value,
                rule: rule
            };

            HostRuleStore.add(new models.BlueprintHostAccessRule().create(accessRule));
            self.navigate({ view: 'host.detail' });
        };

        self.cancelChanges = function (model, evt) {
            self.navigate({ view: 'host.detail' });
        };


    };

    vm.prototype = new base();
    return new vm();
});