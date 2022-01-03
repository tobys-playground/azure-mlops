data "azurerm_client_config" "current" {}

provider "azurerm" { 
  features {}
}

terraform {
  backend "azurerm" {
    resource_group_name      = "tflogs"
    storage_account_name     = "tflogsstorage"
    container_name           = "vhds"
    key                      = "terraform.tfstate"
  }
}

resource "azurerm_resource_group" "example" {
  name     = "example"
  location = "Southeast Asia"
  tags = {
    "stage" = "example"
  }
}

resource "azurerm_application_insights" "example" {
  name                = "example"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  application_type    = "web"
}

resource "azurerm_key_vault" "example" {
  name                = "example"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  tenant_id           = data.azurerm_client_config.current.tenant_id

  sku_name = "standard"

  purge_protection_enabled = true
}

resource "azurerm_storage_account" "example" {
  name                     = "example"
  location                 = azurerm_resource_group.example.location
  resource_group_name      = azurerm_resource_group.example.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_machine_learning_workspace" "example" {
  name                    = "example"
  location                = azurerm_resource_group.example.location
  resource_group_name     = azurerm_resource_group.example.name
  application_insights_id = azurerm_application_insights.example.id
  key_vault_id            = azurerm_key_vault.example.id
  storage_account_id      = azurerm_storage_account.example.id

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_virtual_network" "example" {
  name                = "example"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_subnet" "example" {
  name                 = "example"
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.1.0.0/24"]
}

resource "azurerm_machine_learning_compute_cluster" "example" {
  name                          = "example"
  location                      = "Southeast Asia"
  vm_priority                   = "LowPriority"
  vm_size                       = "Standard_NV6"
  machine_learning_workspace_id = azurerm_machine_learning_workspace.example.id
  subnet_resource_id            = azurerm_subnet.example.id 
  scale_settings {
    min_node_count                       = 1
    max_node_count                       = 2
    scale_down_nodes_after_idle_duration = "PT30S" # 30 seconds
  }

  identity {
    type = "SystemAssigned"
  }
}