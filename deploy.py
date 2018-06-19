#!/usr/bin/env python3

# Python Fabric File For Depoyment of Harmonic IO

from fabric.api import local, env, sudo, run, put, roles
from fabric.decorators import parallel, task

env.user = 'ubuntu'
env.key_filename = '~/.ssh/soberbot94.pem'
env.hosts = open('hostfile', 'r').readlines()
env.roledefs = {
    'master':[env.hosts[0]],
    'workers':[env.hosts[1]]
        }

@task
def ping():
    print("----- Test if the Hosts are Alive ----- \n \n")
    hosts = env.hosts
    for item in list(hosts):
        local('ping -c 5 %s' % item)

@task
def set_hostname_in_master():
    print("\n \n ----- Set Hostname ----- \n \n")
    sudo('hostnamectl set-hostname HIO-master')
    sudo('systemctl restart systemd-hostnamed')
    sudo('echo \'HIO-master\' > /etc/hostname')
    sudo('sed -i \'s/127.0.0.1 localhost.*$/127.0.0.1 localhost HIO-master/\' /etc/hosts')

@task
def set_hostname_in_worker():
    print("\n \n ----- Set Hostname ----- \n \n")
    sudo('hostnamectl set-hostname HIO-worker')
    sudo('systemctl restart systemd-hostnamed')
    sudo('echo \'HIO-worker\' > /etc/hostname')
    sudo('sed -i \'s/127.0.0.1 localhost.*$/127.0.0.1 localhost HIO-worker/\' /etc/hosts')

@task
@parallel
def install_updates():
    print("----- Update Aptitude Packages ----- \n \n")
    sudo('apt-get -y update')

@task
@parallel
def install_python3():
    print("----- Install Python3 & Pip3 ----- \n \n")
    sudo('apt-get -y install python3 python3-pip')

@task
@parallel
def upgrade_pip():
    print("----- Upgrade Pip3 -----\n \n")
    sudo('python3 -m pip install --upgrade pip')

@task
@parallel
def deploy_supervisor():
    print("----- Install Supervisor & Enable it to run at System Boot ----- \n \n")
    sudo('apt-get -y install supervisor')
    sudo('systemctl enable supervisor')

@task
@parallel
def deploy_docker():
    print("----- Install Docker-CE & Enable it to run at System Boot ----- \n \n")
    sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -')
    sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
    sudo('apt-get -y update')
    sudo('apt-get -y install docker-ce')
    sudo('systemctl enable docker')
    sudo('usermod -aG docker %s' % env.user)

@task
def install_requisites():
    set_hostname_in_master()
    set_hostname_in_worker()
    install_updates()
    install_python3()
    upgrade_pip
    deploy_supervisor()
    deploy_docker()

@task
@parallel
def clone_harmonic_repo():
    print("----- Setup Files Required for HarmonicIO ----- \n \n")
    run('mkdir ~/HarmonicIO')
    run('git clone https://github.com/HASTE-project/HarmonicIO.git ~/HarmonicIO')

@task
@parallel
def setup_harmonic():
    print("----- Setup Haronic IO ----- \n \n")
    sudo('pip3 install -e ~/HarmonicIO/.')

@task
@roles('master')
def setup_harmonic_master():
    print("----- Setting Up Harmonic Master Configuration ----- \n \n")
    masterIPv4 = run('ifconfig | grep inet\ addr | awk \'{print $2}\' | cut -d \':\' -f 2')
    run('sed -i \'s/"master_addr".*$/"master_addr": "%s",/\' ~/HarmonicIO/harmonicIO/master/configuration.json' % masterIPv4)

@task
@roles('master')
def setup_supervisor_master():
    print("----- Setting up Supervisor Conf Files For HarmonicIO Master ----- \n \n")
    put('./harmonic_master.conf', '/etc/supervisor/conf.d/harmonic_master.conf', use_sudo=True)

@task
@roles('master')
def prepare_harmonic_master_deployment():
    setup_harmonic_master()
    setup_supervisor_master()

@task
@roles('master')
def deploy_harmonic_master():
    print("----- Starting HarmonicIO Master ----- \n \n")
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

# --------------------------------------------------

@task
@roles('workers')
def setup_harmonic_worker():
    print("----- Setting Up Harmonic Worker Configuration ----- \n \n")
    workerIPv4 = run('ifconfig | grep inet\ addr | awk \'{print $2}\' | cut -d \':\' -f 2')
    run('sed -i \'s/"node_internal_addr".*$/"node_internal_addr": "%s",/\' ~/HarmonicIO/harmonicIO/worker/configuration.json' % workerIPv4)
    run('sed -i \'s/"master_addr".*$/"master_addr": "%s",/\' ~/HarmonicIO/harmonicIO/worker/configuration.json' % masterIPv4)

@task
@roles('workers')
def setup_supervisor_worker():
    print("----- Setting up Supervisor Conf Files For HarmonicIO Worker ----- \n \n")
    put('./harmonic_worker.conf', '/etc/supervisor/conf.d/harmonic_worker.conf', use_sudo=True)

@task
@roles('workers')
def prepare_harmonic_worker_deployment():
    setup_harmonic_worker()
    setup_supervisor_worker()

@task
@roles('workers')
def deploy_harmonic_worker():
    print("----- Starting HarmonicIO Worker ----- \n \n")
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

# --------------------------------------------------

@task
def automate():
    install_requisites()
    clone_harmonic_repo()
    setup_harmonic_repo()
    prepare_harmonic_master_deployment()
    prepare_harmonic_worker_deployment()
    deploy_harmonic_master()
    deploy_harmonic_worker()
