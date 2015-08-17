# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.vm.define 'default' do |default|
    default.vm.box = 'cumulus-vx-2.5.3'

    (1..9).each do |intf|
      default.vm.network "private_network", virtualbox__intnet: "swp#{intf}", auto_config: false
    end

    default.vm.provision :ansible do |ansible|
      ansible.playbook = 'tests/acceptance/playbook/default.yml'
      ansible.sudo = true
    end
  end
end
