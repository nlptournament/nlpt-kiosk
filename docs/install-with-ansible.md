# Install Controller and Kiosks with ansible

As Ansible is the tool of my choice to automate the setup of hard- and software I've created a collection to install a Kiosk-Controller and configure Raspberry Pi's to be used as Kiosks. This collection can be found at githut and ansible-galaxy: [ansible-collection-nlpt_kiosk](https://github.com/nils-ost/ansible-collection-nlpt_kiosk)

Just install it as every other collection on toyour control-node: `ansible-galaxy collection install nils_ost.nlpt_kiosk`

The usage of the two roles (`nils_ost.nlpt_kiosk.controller` and `nils_ost.nlpt_kiosk.rpi`) are described below.

- [Controller Setup](#controller-setup)
  - [host\_vars/kioskcontroller.yml](#host_varskioskcontrolleryml)
  - [play\_kioskcontroller.yml](#play_kioskcontrolleryml)
- [Configure Raspberry Pi as Kiosk](#configure-raspberry-pi-as-kiosk)
  - [group\_vars/kiosks.yml](#group_varskiosksyml)
  - [play\_kiosks.yml](#play_kiosksyml)
- [Both in one Playbook (Full Example)](#both-in-one-playbook-full-example)
  - [hosts.yml](#hostsyml)
  - [host\_vars/kioskcontroller.yml](#host_varskioskcontrolleryml-1)
  - [group\_vars/kiosks.yml](#group_varskiosksyml-1)
  - [play\_nlpt\_kiosk.yml](#play_nlpt_kioskyml)

## Controller Setup

The role `nils_ost.nlpt_kiosk.controller` doesn't do much, it just places a docker-compse.yml onto a server and starts the stack.  
But there are a few variables, you should customize to your needs. Reference the [nils_ost.nlpt_kiosk.controller README](https://github.com/nils-ost/ansible-collection-nlpt_kiosk/blob/main/roles/controller/README.md) for details.

A ansible configuration, for the controller, could look like the following:

### host_vars/kioskcontroller.yml

*define variables for the host*

```yaml
---
ansible_host: 10.13.66.30

docker_daemon_options:
  log-driver: local
  log-opts: {'max-size': '10m'}

nkc_timezone: Europe/Berlin
nkc_controller_release: latest
nkc_controller_auto_upgrade: true
```

### play_kioskcontroller.yml

*playbook for controler setup*

```yaml
---
- name: configures kiosk-controller

  hosts: kioskcontroller
  become: true

  roles:
    - geerlingguy.docker
    - nils_ost.nlpt_kiosk.controller
```

> [!NOTE]
> Remember, that the Kiosk-Controller uses docker to be started. For simplicity the playbook uses `geerlingguy.docker` ansible-role to install and configure docker.

## Configure Raspberry Pi as Kiosk

First of all execute the Baseconfiguration section of [KioskPi](./install-kiosk-rpi-trixie.md) after this the role `nils_ost.nlpt_kiosk.rpi` can do the rest.  
But there are a few variables, you should customize to your needs. Reference the [nils_ost.nlpt_kiosk.rpi README](https://github.com/nils-ost/ansible-collection-nlpt_kiosk/blob/main/roles/rpi/README.md) for details.

A ansible configuration, for your Kiosk Pi's, could look like the following:

### group_vars/kiosks.yml

*define variables for a group of hosts, that contains all your Pi's*

```yaml
---
ansible_user: pi
nkc_timezone: Europe/Berlin
nkc_kiosk_enable_vnc: true
nkc_kiosk_ntp_server: your.controller.server
```

### play_kiosks.yml

*playbook to configure all Kiosks*

```yaml
---
- name: configures Raspberry Pis as kiosks

  hosts: kiosks
  become: true

  roles:
    - nils_ost.nlpt_kiosk.rpi
```

## Both in one Playbook (Full Example)

*the target is to have one playbook, that installs the Controller and configures all Kiosks*

### hosts.yml

```yaml
---
server:
  hosts:
    kioskcontroller:

kiosks:
  hosts:
    bpi1:
      ansible_host: 10.13.66.31
    bpi2:
      ansible_host: 10.13.66.32
    bpi3:
      ansible_host: 10.13.66.33
```

### host_vars/kioskcontroller.yml

```yaml
---
ansible_host: 10.13.66.30

docker_daemon_options:
  log-driver: local
  log-opts: {'max-size': '10m'}

nkc_timezone: Europe/Berlin
nkc_controller_release: latest
nkc_controller_auto_upgrade: true
```

### group_vars/kiosks.yml

```yaml
---
ansible_user: pi
nkc_timezone: Europe/Berlin
nkc_kiosk_enable_vnc: true
nkc_kiosk_ntp_server: your.controller.server
```

### play_nlpt_kiosk.yml

```yaml
---
- name: configures kiosk-controller

  hosts: kioskcontroller

  roles:
    - geerlingguy.docker
    - nils_ost.nlpt_kiosk.controller

- name: configures Raspberry Pis as kiosks

  hosts: kiosks
  become: true

  roles:
    - nils_ost.nlpt_kiosk.rpi
```

> [!NOTE]
> This example could be further optimized e.g. by placing `nkc_timezone` definition to `group_vars/all.yml` but you get the idea.
