require_relative '../spec_helper'

%w(lo eth0 swp1 swp2 swp3).each do |intf|
  describe interface(intf) do
    it { should exist }
    it { should be_up } if intf != 'lo'
  end

  describe file("/etc/network/interfaces.d/#{intf}") do
    it { should be_file }
  end
end

describe interface('swp4') do
  it { should_not be_up }
end

describe file('/etc/network/interfaces/swp4') do
  it { should_not exist }
end
