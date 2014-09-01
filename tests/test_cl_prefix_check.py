import mock
from nose.tools import set_trace
from dev_modules.cl_prefix_check import main, \
    loop_route_check
from asserts import assert_equals

def mod_args(arg):
    values = {
        'prefix': '1.1.1.1/24',
        'poll_interval': '1',
        'timeout': '2',
        'state': 'present'
    }
    return values[arg]


@mock.patch('dev_modules.cl_prefix_check.loop_route_check')
@mock.patch('dev_modules.cl_prefix_check.AnsibleModule')
def test_module_args(mock_module,
                     mock_loop_route_check):
    """
    cl_prefix_check: test module arguments
    """
    instance = mock_module.return_value
    instance.params.get.side_effect = mod_args
    main()
    mock_module.assert_called_with(
        argument_spec={'prefix': {'required': True, 'type': 'str'},
                       'poll_interval': {'type':'int', 'default': 1},
                       'timeout': {'type': 'int', 'default': 2},
                       'state': {'type': 'str',
                                 'default': 'present',
                                 'choices': ['present', 'absent']}})

def mock_loop_check_arg(arg):
    values = {
        'prefix': '10.1.1.1',
        'state': 'present',
        'timeout': 10,
        'poll_interval': '1'
    }
    return values[arg]

@mock.patch('dev_modules.cl_prefix_check.run_cl_cmd')
@mock.patch('dev_modules.cl_prefix_check.AnsibleModule')
def test_loop_route_check_state_present(mock_module,
                                        mock_run_cl_cmd):
    instance = mock_module.return_value
    instance.params.get.side_effect = mock_loop_check_arg
    mock_run_cl_cmd.return_value = ['something']
    assert_equals(loop_route_check(instance), True)
