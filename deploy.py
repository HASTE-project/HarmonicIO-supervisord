#!/usr/bin/env python3

# Python Fabric File For Depoyment of Harmonic IO

from fabric.api import local, env, sudo, run, put, roles

env.user = 'ubuntu'
env.key_filename = '~/.ssh/soberbot94.pem'
env.hosts = open('hostfile', 'r').readlines()
env.roledefs = {
    'master':[env.hosts[0]],
    'workers':[env.hosts[1]]
        }

def ping():
    print("----- Test if the Hosts are Alive ----- \n \n")
    hosts = env.hosts
    for item in list(hosts):
        local('ping -c 5 %s' % item)

def install_updates():
    print("----- Update Aptitude Packages ----- \n \n")
    sudo('apt-get -y update')

def install_python3():
    print("----- Install Python3 & Pip3 ----- \n \n")
    sudo('apt-get -y install python3 python3-pip')

def deploy_supervisor():
    print("----- Install Supervisor & Enable it to run at System Boot ----- \n \n")
    sudo('apt-get -y install supervisor')
    sudo('systemctl enable supervisor')

def deploy_docker():
    print("----- Install Docker-CE & Enable it to run at System Boot ----- \n \n")
    sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -')
    sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
    sudo('apt-get -y update')
    sudo('apt-get -y install docker-ce')
    sudo('systemctl enable docker')
    sudo('usermod -aG docker %s' % env.user)

def install_requisites():
    install_updates()
    install_python3()
    deploy_supervisor()
    deploy_docker()

def clone_harmonic_repo():
    print("----- Setup Files Required for HarmonicIO ----- \n \n")
    run('mkdir ~/Workdir')
    run('git clone https://github.com/HASTE-project/HarmonicIO.git ~/Workdir')

def setup_harmonic():
    print("----- Setup Haronic IO ----- \n \n")
    sudo('pip3 install -e ~/Workdir/.')

@roles('master')
def setup_harmonic_master():
    print("----- Setting Up Harmonic Master Configuration ----- \n \n")
    run('sed -i \'s/"master_addr".*$/"master_addr": "192.168.1.33",/\' ~/Workdir/harmonicIO/master/configuration.json')

@roles('master')
def setup_supervisor_master():
    print("----- Setting up Supervisor Conf Files For HarmonicIO Master ----- \n \n")
    put('./harmonic_master.conf', '/etc/supervisor/conf.d/harmonic_master.conf', use_sudo=True)

@roles('master')
def prepare_harmonic_master_deployment():
    clone_harmonic_repo()
    setup_harmonic()
    setup_harmonic_master()
    setup_supervisor_master()

@roles('master')
def deploy_harmonic_master():
    print("----- Starting HarmonicIO Master ----- \n \n")
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

# --------------------------------------------------

@roles('workers')
def setup_harmonic_worker():
    print("----- Setting Up Harmonic Worker Configuration ----- \n \n")
    run('sed -i \'s/"node_internal_addr".*$/"node_internal_addr": "192.168.1.5",/\' ~/Workdir/harmonicIO/worker/configuration.json')
    run('sed -i \'s/"master_addr".*$/"master_addr": "192.168.1.33",/\' ~/Workdir/harmonicIO/worker/configuration.json')

@roles('workers')
def setup_supervisor_worker():
    print("----- Setting up Supervisor Conf Files For HarmonicIO Worker ----- \n \n")
    put('./harmonic_worker.conf', '/etc/supervisor/conf.d/harmonic_worker.conf', use_sudo=True)

@roles('workers')
def prepare_harmonic_worker_deployment():
    clone_harmonic_repo()
    setup_harmonic()
    setup_harmonic_worker()
    setup_supervisor_worker()

@roles('workers')
def deploy_harmonic_worker():
    print("----- Starting HarmonicIO Worker ----- \n \n")
    sudo('supervisorctl reread')
    sudo('supervisorctl update')
