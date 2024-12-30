# tflint-ignore: terraform_module_provider_declaration, terraform_output_separate, terraform_variable_separate
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

locals {
  resource_tags = merge(
    {
      "deployed-by" = "terraform-module-simplelinuxvm"
    },
    var.custom_tags
  )
  rg_name      = "${var.resource_prefix}-rg01"
  network_name = "${var.resource_prefix}-vnet01"
  vm_name      = "${var.resource_prefix}-vm01"
  bastion_name = "${var.resource_prefix}-bast01"
  nsg_name     = "${var.resource_prefix}-nsg01"
}

resource "azurerm_resource_group" "this" {
  name     = local.rg_name
  location = var.deployment_region
  tags     = local.resource_tags
}

resource "azurerm_virtual_network" "this" {
  name                = local.network_name
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.resource_tags
}

resource "azurerm_subnet" "this" {
  name                 = "${local.network_name}-subnet01"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "this" {
  allocation_method   = "Dynamic"
  location            = azurerm_resource_group.this.location
  name                = "${local.vm_name}-ip01"
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "Basic"
  tags                = local.resource_tags
}

resource "azurerm_network_interface" "this" {
  name                = "${local.vm_name}-nic01"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.resource_tags

  ip_configuration {
    name                          = "${local.vm_name}-ipcfg01"
    subnet_id                     = azurerm_subnet.this.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.this.id
  }
}

resource "azurerm_network_security_group" "this" {
  name                = local.nsg_name
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.resource_tags

  security_rule {
    name                       = "sshAllowFromHome"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = join(", ", var.whitelisted_ip_ranges)
    destination_address_prefix = join(", ", azurerm_subnet.this.address_prefixes)
  }
}

resource "azurerm_subnet_network_security_group_association" "this" {
  subnet_id                 = azurerm_subnet.this.id
  network_security_group_id = azurerm_network_security_group.this.id
}

resource "azurerm_virtual_machine" "this" {
  name                  = local.vm_name
  location              = azurerm_resource_group.this.location
  resource_group_name   = azurerm_resource_group.this.name
  network_interface_ids = [azurerm_network_interface.this.id]
  vm_size               = "Standard_B1s"
  tags                  = local.resource_tags

  delete_os_disk_on_termination = true

  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
  storage_os_disk {
    name              = "${local.vm_name}-disk01"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }
  os_profile {
    computer_name  = local.vm_name
    admin_username = "user01"
  }
  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      key_data = file(var.ssh_public_key_path)
      path     = "/home/user01/.ssh/authorized_keys"
    }
  }
}