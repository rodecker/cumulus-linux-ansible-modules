require_relative '../spec_helper'

intf_dir = File.join('', 'etc', 'network', 'interfaces.d')

# classic bridge driver
describe file("#{intf_dir}/br0") do
  it { should be_file }
  its(:content) { should match(/iface br0/) }
  its(:content) { should match(/bridge-ports swp10 glob swp11-12 swp13/) }
  its(:content) { should match(/bridge-stp yes/) }
end

describe file("#{intf_dir}/br1") do
  it { should be_file }
  its(:content) { should match(/iface br1/) }
  its(:content) { should match(/bridge-ports glob swp14-15/) }
  its(:content) { should match(/bridge-stp no/) }
  its(:content) { should match(/mstpctl-treeprio 4096/) }
  its(:content) { should match(%r{address 10.0.0.1/24 192.168.1.0/16 2001:db8:abcd::/48}) }
end

# New bridge driver
describe file("#{intf_dir}/bridge2") do
  it { should be_file }
  its(:content) { should match(/iface bridge2/) }
  its(:content) { should match(/bridge-ports glob swp16-17/) }
  its(:content) { should match(/bridge-stp yes/) }
end

describe file("#{intf_dir}/bridge3") do
  it { should be_file }
  its(:content) { should match(/iface bridge3/) }
  its(:content) { should match(/bridge-vlan-aware yes/) }
  its(:content) { should match(/bridge-ports glob swp18-19/) }
  its(:content) { should match(/bridge-stp no/) }
  its(:content) { should match(/mtu 9000/) }
  its(:content) { should match(/mstpctl-treeprio 4096/) }
  its(:content) { should match(/bridge-pvid 1/) }
  its(:content) { should match(/bridge-vids 1-4094/) }
  its(:content) { should match(%r{address 10.0.100.1/24 192.168.100.0/16 2001:db8:1234::/48}) }
end
