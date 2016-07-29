require_relative '../spec_helper'

intf_dir = File.join('', 'etc', 'network', 'interfaces.d')

# The manifest should have created the .d directory
describe file(intf_dir) do
  it { should be_directory }
end

# Should have been created by the cumulus_bond resource
describe file("#{intf_dir}/bond0") do
  it { should be_file }
  its(:content) { should match(/iface bond0/) }
  its(:content) { should match(/bond-slaves glob swp5-6 swp7/) }
end

describe file("#{intf_dir}/bond1") do
  it { should be_file }
  # its(:content) { should match(/iface bond1 inet static/) }
  its(:content) { should match(/iface bond1/) }
  its(:content) { should match(/bond-slaves glob swp8-9/) }
  its(:content) { should match(/mtu 9000/) }
  its(:content) { should match(/bond-miimon 99/) }
  its(:content) { should match(/bond-lacp-rate 1/) }
  its(:content) { should match(/bond-min-links 2/) }
  its(:content) { should match(/bridge-vids 1-4094/) }
  its(:content) { should match(/bridge-pvid 1/) }
  its(:content) { should match(/alias bond number 1/) }
  its(:content) { should match(/bond-mode balance-alb/) }
  its(:content) { should match(/bond-xmit-hash-policy layer2/) }
  its(:content) { should match(%r{address 10.0.0.1/24 192.168.1.0/16 2001:db8:abcd::/48}) }
  its(:content) { should match(/address-virtual 00:00:5e:00:01:01 192.168.20.1/) }
  its(:content) { should match(/mstpctl-portnetwork yes/) }
  its(:content) { should match(/mstpctl-bpduguard yes/) }
end
