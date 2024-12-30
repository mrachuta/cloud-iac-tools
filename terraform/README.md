# General info
Ansible configuration to deploy a simple stack on Azure. It consists of:
- resource group
- virtual network
- subnetwork
- public ip address
- network interface
- network security group
- virtual machine

Biggest challenges:

* no challenges as it is most popular and well-documentend IAC tool

# Preparation

1) Install terraform (Debian):
    ```
    wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install terraform
    ```
2) Create configuration file and replace placeholders:
    ```
    mv variables.auto.example.tfvars variables.auto.tfvars
    vim variables.auto.tfvars
    ```
3) Create .env file with following data:
   ```
   cat <<\EOT >.env
   ARM_TENANT_ID="<YOUR_TENANT_ID>"
   ARM_SUBSCRIPTION_ID="<YOUR_SUBSCRIPTION_ID>"
   EOT
   ```

# Usage

1) To deploy resources, first, login to your Azure account using cli and optionally set a subscription (if you have more than one associated with your account) using the following commands:
    ```
    az login
    az account set --subscription "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    ```
    Then deploy resources:
    ```
    terraform plan
    terraform apply -auto-approve
    ```
    NOTE: It will ask you to create secret passphrase to secure your configuration and secrets
2) To destroy resources, run the following command:
    ```
    terraform destroy
    ```
