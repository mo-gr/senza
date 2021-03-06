
from senza.utils import ensure_keys, named_value


def format_params(args):
    items = [(key, val) for key, val in args.__dict__.items() if key not in ('region', 'version')]
    return ', '.join(['{}: {}'.format(key, val) for key, val in items])


def get_default_description(info, args):
    return '{} ({})'.format(info['StackName'].title().replace('-', ' '), format_params(args))


def component_configuration(definition, configuration, args, info, force):
    # add info as mappings
    # http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html
    definition = ensure_keys(definition, "Mappings", "Senza", "Info")
    definition["Mappings"]["Senza"]["Info"] = info

    # define parameters
    # http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html
    if "Parameters" in info:
        definition = ensure_keys(definition, "Parameters")
        default_parameter = {
            "Type": "String"
        }
        for parameter in info["Parameters"]:
            name, value = named_value(parameter)
            value_default = default_parameter.copy()
            value_default.update(value)
            definition["Parameters"][name] = value_default

    if 'Description' not in definition:
        # set some sane default stack description
        definition['Description'] = get_default_description(info, args)

    # ServerSubnets
    for region, subnets in configuration.get('ServerSubnets', {}).items():
        definition = ensure_keys(definition, "Mappings", "ServerSubnets", region)
        definition["Mappings"]["ServerSubnets"][region]["Subnets"] = subnets

    # LoadBalancerSubnets
    for region, subnets in configuration.get('LoadBalancerSubnets', {}).items():
        definition = ensure_keys(definition, "Mappings", "LoadBalancerSubnets", region)
        definition["Mappings"]["LoadBalancerSubnets"][region]["Subnets"] = subnets

    # LoadBalancerInternalSubnets
    for region, subnets in configuration.get('LoadBalancerInternalSubnets', {}).items():
        definition = ensure_keys(definition, "Mappings", "LoadBalancerInternalSubnets", region)
        definition["Mappings"]["LoadBalancerInternalSubnets"][region]["Subnets"] = subnets

    # Images
    for name, image in configuration.get('Images', {}).items():
        for region, ami in image.items():
            definition = ensure_keys(definition, "Mappings", "Images", region, name)
            definition["Mappings"]["Images"][region][name] = ami

    return definition
