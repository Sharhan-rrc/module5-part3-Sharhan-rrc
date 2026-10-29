# Optional reproducible VM deployment for Part 3, separate from Docker Desktop.
Vagrant.configure("2") do |config|
  config.vm.box = "eurolinux-vagrant/centos-stream-9"
  config.vm.hostname = "sharhankaji-module5"
  config.vm.network "private_network", ip: "192.168.56.55"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 4096
    vb.cpus = 2
    vb.gui = false
  end
  config.vm.provision "shell", path: "provision.sh"
end
