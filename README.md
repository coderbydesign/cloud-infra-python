# CloudInfraClient

A python client which provides an interface to cloud.redhat RBAC and entitlements infrastructure services.

## Installation

```shell
pip install https://github.com/RedHatInsights/cloud-infra-ruby
```

## Usage

The following environment variables are required to be set, or default will be used where applicable:
```
REDIS_HOST # default is 127.0.0.1
REDIS_PORT # default is 6379
REDIS_DB # default is 0
REDIS_PASSWORD # no default
CACHE_HOST # no default
```

```python
# require the client module
from cloud.infra.client import CloudInfraClient

# create a new client
platform_client = CloudInfraClient()

# get all RBAC access for a principal/application
rbac_access = platform_client.rbac_access(identity_header, application)
# check if the principal has RBAC access to the application
has_rbac_access = platform_client.has_rbac_access(identity_header, application)

# get all entitlements for a principal
entitlements = platform_client.entitlements(identity_header)
# check if the principal has entitlements access to the bundle
has_entitlements_access = platform_client.has_entitlements_access(identity_header, bundle)
```

## License

The gem is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
