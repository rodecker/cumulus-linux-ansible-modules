require_relative '../spec_helper'

intf_dir = File.join('', 'etc', 'network', 'interfaces.d')

# Should exist
%w( eth0 lo ).each do |intf|
  describe file("#{intf_dir}/#{intf}") do
    it { should be_file }
  end
end

# Should have been configured
describe file("#{intf_dir}/swp1") do
  it { should be_file }
  its(:content) { should match(/iface swp1/) }
end

describe file("#{intf_dir}/swp2") do
  it { should be_file }
  its(:content) { should match(/iface swp2/) }
  its(:content) { should match(/address 192.168.200.1 2001:db8:5678::/) }
  its(:content) { should match(/mtu 9000/) }
  its(:content) { should match(/bridge-vids 1-4094/) }
  its(:content) { should match(/bridge-pvid 1/) }
  its(:content) { should match(/link-speed 1000/) }
  its(:content) { should match(/link-duplex full/) }
  its(:content) { should match(/alias interface swp2/) }
  its(:content) { should match(/mstpctl-portnetwork yes/) }
  its(:content) { should match(/mstpctl-bpduguard yes/) }
  its(:content) { should match(/address-virtual/) }
end
