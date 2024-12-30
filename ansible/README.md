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
* no automatic dependecy management (dependencies between cloud objects; you need to create and delete them in a logical order),
* handmade logic to destroy components (I found no ready-to-use solutions)
  * antoher idea for bigger stacks is to parametrise state (present or absent), then to create each task in separate file, whose name starts with number 001-999. Then, depending on case, tasks could be imported as sorted (state: present) or reverse sorted (state:absent)
  * it's just theory, it was not tested yet

# Preparation

1) Install required packages in virtualenv:
    ```
    mkvirtualenv ansible
    pip3 install -r requirements.txt
    ```
2) Install Ansible collection & required packages:
    ```
    ansible-galaxy collection install azure.azcollection
    pip3 install -r ~/.ansible/collections/ansible_collections/azure/azcollection/requirements.txt
    ```
3) Create file with variables and replace placeholders:
    ```
    mv group_vars/all-example.yml group_vars/all.yml
    vim group_vars/all.yml
    ```

# Usage

1) To deploy resources, first, login to your Azure account using cli and optionally set a subscription (if you have more than one associated with your account) using the following commands:
    ```
    az login
    az account set --subscription "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    ```
    Then deploy resources:
    ```
    ansible-playbook main.yml
    ```
2) To destroy resources, run the following command:
    ```
    ansible-playbook main.yml --tags destroy-all
    ```
