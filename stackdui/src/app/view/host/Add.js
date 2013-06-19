Ext.define('stackdio.view.host.Add', {
    extend  : 'Ext.window.Window',
    alias: 'widget.addHost',
    
    width   : 800,
    title   : 'Stack Host',
    modal   : true,
    closable: true,
    closeAction: 'hide',
    defaultFocus: 'host-count',

    defaults: {
        padding: '10'
    },

    layout: 'fit',

    items: [{
        xtype: 'form',
        id: 'host-form',
        border: false,
        layout: 'anchor',
        defaults: {
            anchor: '100%'
        },
        items: [
        {
            xtype:        'combo',
            name:         'cloud_profile',
            hideLabel:    false,
            fieldLabel:   'Profile',
            labelWidth:   110,
            store:        'AccountProfiles',
            displayField: 'title',
            valueField:   'id',
            queryMode:    'local',
            editable:     false
        },{
            xtype:        'multiselect',
            name:         'role',
            hideLabel:    false,
            fieldLabel:   'Role',
            labelWidth:   110,
            store:        'Roles',
            displayField: 'title',
            valueField:   'id',
            queryMode:    'local',
            editable:     false
        },{
            xtype:'textfield',
            id: 'host-count',
            name: 'count',
            fieldLabel: 'Count',
            labelWidth: 110
        },{
            xtype:        'combo',
            id:           'host-instance-size',
            name:         'instance_size',
            hideLabel:    false,
            fieldLabel:   'Instance Size',
            labelWidth:   110,
            store:        'InstanceSizes',
            displayField: 'title',
            valueField:   'id',
            queryMode:    'local',
            editable:     false
        },{
            xtype:'textfield',
            id: 'host-security-groups',
            name: 'security_groups',
            fieldLabel: 'Security Groups',
            labelWidth: 110
        },{
            xtype:'textfield',
            id: 'host-hostname',
            name: 'hostname',
            fieldLabel: 'Host Pattern',
            labelWidth: 110
        }]
    }],

    buttons: [{
        text: 'Cancel',
        iconCls: 'cancel-icon',
        handler: function (btn) {
            btn.up('window').hide();
        }
    },{
        text: 'Save',
        id: 'save-stack-host',
        iconCls: 'save-icon'
    }]
});
