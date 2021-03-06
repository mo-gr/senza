'''
Elasticache cluster running multiple redis nodes, with replication / HA
'''

from clickclick import warning
from senza.utils import pystache_render

from ._helper import prompt, check_security_group, check_value


TEMPLATE = '''
# basic information for generating and executing this definition
SenzaInfo:
  StackName: {{ application_id }}

# a list of senza components to apply to the definition
SenzaComponents:

  # this basic configuraation is required for the other components
  - Configuration:
      Type: Senza::StupsAutoConfiguration # auto-detect network setup

  - {{ application_id }}:
      Type: Senza::RedisCluster
      CacheNodeType: {{ instance_type }}
      NumberOfNodes: {{ number_of_nodes }}
      SecurityGroups:
        - redis-{{ application_id }}

'''


def gather_user_variables(variables, region):
    # maximal 32 characters because of the loadbalancer-name
    prompt(variables, 'application_id', 'Application ID', default='hello-world',
           value_proc=check_value(18, '^[a-zA-Z][-a-zA-Z0-9]*$'))
    prompt(variables, 'instance_type', 'EC2 instance type', default='cache.m3.medium')
    prompt(variables, 'number_of_nodes', 'Number of nodes in cluster', default='2',
           value_proc=check_value(1, '^[2-5]$'))

    sg_name = 'redis-{}'.format(variables['application_id'])

    rules_missing = check_security_group(sg_name, [('tcp', 6379)], region, allow_from_self=True)
    if ('tcp', 6379) in rules_missing:
        warning('Security group {} does not allow tcp/6379 access yet, you will not be able to access redis'.format(
            sg_name))

    return variables


def generate_definition(variables):
    definition_yaml = pystache_render(TEMPLATE, variables)
    return definition_yaml
