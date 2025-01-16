# General info
Ansible configuration to deploy a simple stack on Azure. It consists of:
- resource group
- virtual network
- subnetwork
- public ip address
- network interface
- network security group
- virtual machine

Additional information:

Configuration was created using a template to speed-up deployment:
```
pulumi new azure-python --name az-poc --description "Pulumi Azure deployment using python" --stack dev
```

Biggest challenges:

* sometimes complex logic for non-professional programmers (.apply() method to get resource attributes)
* quickstart is not as easy as expected (Pulumi tries to force you to use Pulumi Cloud)

# Preparation

1) Install pulumi:
    ```
    curl -fsSL https://get.pulumi.com | sh
    ```
2) Configure state file to be stored in local machine:
    ```
    pulumi login --local
    ```
3) Install required packages in virtualenv:
    ```
    mkvirtualenv pulumi
    pip3 install -r requirements.txt
    ```
4) Create configuration file and replace placeholders:
    ```
    mv Pulumi.dev-example.yaml Pulumi.dev.yaml
    vim Pulumi.dev.yaml
    ```

# Usage

1) To deploy resources, first, login to your Azure account using cli and optionally set a subscription (if you have more than one associated with your account) using the following commands:
    ```
    az login
    az account set --subscription "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    ```
    Then deploy resources:
    ```
    pulumi up -s dev
    ```
    NOTE: It will ask you to create secret passphrase to secure your configuration and secrets
2) To destroy resources, run the following command:
    ```
    pulumi destroy -s dev
    ```
