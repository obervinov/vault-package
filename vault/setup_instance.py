"""
This script contains functions for the typical automatic configuration of a new storage instance.
- creating a new approle
- loading project policy from hcl file
"""
import os
import argparse
from tools.configurator import VaultConfigurator

token = os.environ.get(
    'VAULT_TOKEN',
    None
)
address = os.environ.get(
    'VAULT_ADDR',
    None
)

argparser = argparse.ArgumentParser()

argparser.add_argument(
    "-nc",
    "--namespace.create",
    help="If you need to create a new namespace.",
    type=bool,
    default=False
)
argparser.add_argument(
    "-nn",
    "--namespace.name",
    help="The name of the target namespace to configure",
    type=str,
    required=True,
)
argparser.add_argument(
    "-an",
    "--approle.name",
    help="Name of the app-role. Usually coincides with the name of the project",
    type=str,
    required=True,
)
argparser.add_argument(
    "-ac",
    "--approle.create",
    help="If you need to create a new app-role.",
    type=bool,
    default=True
)
argparser.add_argument(
    "-ac",
    "--approle.description",
    help="Description by whom and when was approle created.",
    type=str,
    default=None
)
argparser.add_argument(
    "-pn",
    "--policy.name",
    help="Name of the policy to link to the approle",
    type=str,
    required=True,
)
argparser.add_argument(
    "-pp",
    "--policy.path",
    help="Path of the new policy",
    type=str,
    required=True,
)
argparser.add_argument(
    "-pc",
    "--policy.create",
    help="If you need to create a new policy.",
    type=bool,
    default=False
)
args = argparser.parse_args()


configurator = VaultConfigurator(
    address,
    token
)

if args.namespace.create:
    namespace = configurator.create_namespace(
        name=args.namespace.name
    )

if args.policy.create:
    policy = configurator.create_policy(
        name=args.policy.name,
        path=args.policy.path
    )

if args.approle.create:
    approle = configurator.create_approle(
        name=args.approle.name,
        path=namespace,
        policy=policy,
        descritpion=args.approle.description
    )
    print(f"AppRole for connection: {approle}")
