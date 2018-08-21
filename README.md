This repo is deprecated, please use the Ansible scripts instead.


# Python Fabric Script For Deploying HarmonicIO Master & Worker Nodes Along With Supervisord Services
---

## Requirements

* Git

* Python3
---

## Edit Hosts File

Add host IP addresses as plain text, each line will have only one IPv4 address

```
	192.168.x.x
	130.238.x.x
```

### Map Hosts To Specific Roles

**env.hosts** is a list of all the IPs in the Host file, 
so different list elements can be mapped to their respective role definitions **env.roledefs**

```py
env.roledefs = {
    'master':[env.hosts[0]],
    'workers':[env.hosts[1]]
	}
```
---

## Run Specific Tasks From The Fab File

```sh
	fab -f ./deploy.py TASK_NAME
```

Here **-f** flag is used to specify the fabric file.
