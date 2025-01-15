"""An Azure RM Python Pulumi program"""

import pulumi
from yaml import safe_load as parseYaml
from pulumi_azure_native import resources, network, compute

# Generate variables
config = pulumi.Config()
try:
    resource_prefix = config.get("resourcePrefix")
    resource_tags = parseYaml(config.get("resourceTags"))
    deployment_region = config.get("deploymentRegion")
    whitelisted_ip_ranges = parseYaml(config.get("whitelistedIpRanges"))
    ssh_public_key_path = config.get("sshPublicKeyPath")
except KeyError or AttributeError as err:
    raise Exception(f"Error in configuration: \n{err}!")

rg_name = f"{resource_prefix}-rg01"
network_name = f"{resource_prefix}-vnet01"
vm_name = f"{resource_prefix}-vm01"
nsg_name = f"{resource_prefix}-nsg01"
resource_tags.update({"deployed-by": "pulumi-module-simplelinuxvm"})
# Read ssh pubkey
with open(ssh_public_key_path, "r") as f:
    ssh_public_key = f.read()

# Resources creation
my_rg = resources.ResourceGroup(
    rg_name, resource_group_name=rg_name, location=deployment_region, tags=resource_tags
)

my_network = network.VirtualNetwork(
    network_name,
    virtual_network_name=network_name,
    resource_group_name=my_rg.name,
    location=my_rg.location,
    address_space={
        "address_prefixes": [
            "10.0.0.0/16",
        ]
    },
    tags=resource_tags,
    opts=pulumi.ResourceOptions(delete_before_replace=True)
)

my_nsg = network.NetworkSecurityGroup(
    nsg_name,
    network_security_group_name=nsg_name,
    resource_group_name=my_rg.name,
    location=my_rg.location,
    security_rules=[
        {
            "name": "sshAllowFromHome",
            "priority": 100,
            "direction": "Inbound",
            "access": "Allow",
            "protocol": "TCP",
            "source_port_range": "*",
            "destination_port_range": "22",
            "source_address_prefixes": whitelisted_ip_ranges,
            "destination_address_prefixes": ["10.0.1.0/24"],
        },
    ],
    tags=resource_tags,
    opts=pulumi.ResourceOptions(delete_before_replace=True)
)

my_subnet = network.Subnet(
    f"{network_name}-subnet01",
    subnet_name=f"{network_name}-subnet01",
    address_prefix="10.0.1.0/24",
    resource_group_name=my_rg.name,
    virtual_network_name=my_network.name,
    network_security_group={"id": my_nsg.id},
    opts=pulumi.ResourceOptions(delete_before_replace=True)
)

my_public_ip = network.PublicIPAddress(
    f"{vm_name}-ip01",
    public_ip_address_name=f"{vm_name}-ip01",
    resource_group_name=my_rg.name,
    location=my_rg.location,
    public_ip_allocation_method="Dynamic",
    sku={"name": "Basic"},
    tags=resource_tags,
    opts=pulumi.ResourceOptions(delete_before_replace=True)
)

my_nic = network.NetworkInterface(
    f"{vm_name}-nic01",
    network_interface_name=f"{vm_name}-nic01",
    resource_group_name=my_rg.name,
    location=my_rg.location,
    ip_configurations=[
        {
            "name": f"{vm_name}-ipcfg01",
            "subnet": {"id": my_subnet.id},
            "public_ip_address": {"id": my_public_ip.id},
            "private_ip_allocation_method": "Dynamic",
        },
    ],
    tags=resource_tags,
    opts=pulumi.ResourceOptions(delete_before_replace=True)
)

my_vm = compute.VirtualMachine(
    vm_name,
    vm_name=vm_name,
    location=my_rg.location,
    resource_group_name=my_rg.name,
    network_profile={
        "network_interfaces": [
            {
                "id": my_nic.id,
            }
        ]
    },
    hardware_profile={"vm_size": "Standard_B1s"},
    storage_profile={
        "os_disk": {
            "create_option": "FromImage",
            "delete_option": "Delete",
            "caching": "ReadWrite",
            "name": f"{vm_name}-disk01",
            "managed_disk": {"storage_account_type": "Standard_LRS"},
        },
        "image_reference": {
            "publisher": "Canonical",
            "offer": "0001-com-ubuntu-server-jammy",
            "sku": "22_04-lts",
            "version": "latest",
        },
    },
    os_profile={
        "admin_username": "user01",
        "computer_name": vm_name,
        "linux_configuration": {
            "disable_password_authentication": True,
            "ssh": {
                "public_keys": [
                    {
                        "key_data": ssh_public_key,
                        "path": "/home/user01/.ssh/authorized_keys",
                    }
                ]
            },
        },
    },
    opts=pulumi.ResourceOptions(delete_before_replace=True)
)

# Outputs
pulumi.export(
    "vm_ip_address: ",
    my_vm.id.apply(
        lambda id: network.get_public_ip_address_output(
            resource_group_name=my_rg.name,
            public_ip_address_name=my_public_ip.name,
        )
    ).ip_address,
)
