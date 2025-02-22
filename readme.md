Creation params:

Get to http://xo-cslab.dei.uc.pt/rest/v0/pools/6ddb8190-651e-f8ed-7fab-5e5a225857b7/actions/create_vm
{
    "params": {
        "affinity": {
            "type": "string",
            "optional": true
        },
        "auto_poweron": {
            "type": "boolean",
            "optional": true
        },
        "boot": {
            "type": "boolean",
            "default": false
        },
        "clone": {
            "type": "boolean",
            "default": true
        },
        "install": {
            "type": "object",
            "optional": true,
            "properties": {
                "method": {
                    "enum": [
                        "cdrom",
                        "network"
                    ]
                },
                "repository": {
                    "type": "string"
                }
            }
        },
        "memory": {
            "type": "integer",
            "optional": true
        },
        "name_description": {
            "type": "string",
            "minLength": 0,
            "optional": true
        },
        "name_label": {
            "type": "string"
        },
        "template": {
            "type": "string"
        }
    }
}


Actions VM:
[
    "/rest/v0/vms/41a7d793-a070-e561-083c-4e6dcb2d7418/actions/clean_reboot",
    "/rest/v0/vms/41a7d793-a070-e561-083c-4e6dcb2d7418/actions/clean_shutdown",
    "/rest/v0/vms/41a7d793-a070-e561-083c-4e6dcb2d7418/actions/hard_reboot",
    "/rest/v0/vms/41a7d793-a070-e561-083c-4e6dcb2d7418/actions/hard_shutdown",
    "/rest/v0/vms/41a7d793-a070-e561-083c-4e6dcb2d7418/actions/snapshot",
    "/rest/v0/vms/41a7d793-a070-e561-083c-4e6dcb2d7418/actions/start"
]

Actions Pool:
[
    "/rest/v0/pools/6ddb8190-651e-f8ed-7fab-5e5a225857b7/actions/create_vm",
    "/rest/v0/pools/6ddb8190-651e-f8ed-7fab-5e5a225857b7/actions/emergency_shutdown",
    "/rest/v0/pools/6ddb8190-651e-f8ed-7fab-5e5a225857b7/actions/rolling_reboot",
    "/rest/v0/pools/6ddb8190-651e-f8ed-7fab-5e5a225857b7/actions/rolling_update"
]


Actions Network:
Não tem