#!/usr/bin/env python
import redis
import os
import base64
import json
import requests

# usage
# from packages.cloud.infra.client import CloudInfraClient

# identity_header = 'eyJlbnRpdGxlbWVudHMiOnsiaW5zaWdodHMiOnsiaXNfZW50aXRsZWQiOnRydWUsImlzX3RyaWFsIjpmYWxzZX0sImNvc3RfbWFuYWdlbWVudCI6eyJpc19lbnRpdGxlZCI6dHJ1ZSwiaXNfdHJpYWwiOmZhbHNlfSwibWlncmF0aW9ucyI6eyJpc19lbnRpdGxlZCI6dHJ1ZSwiaXNfdHJpYWwiOmZhbHNlfSwiYW5zaWJsZSI6eyJpc19lbnRpdGxlZCI6dHJ1ZSwiaXNfdHJpYWwiOmZhbHNlfSwidXNlcl9wcmVmZXJlbmNlcyI6eyJpc19lbnRpdGxlZCI6dHJ1ZSwiaXNfdHJpYWwiOmZhbHNlfSwib3BlbnNoaWZ0Ijp7ImlzX2VudGl0bGVkIjp0cnVlLCJpc190cmlhbCI6ZmFsc2V9LCJzbWFydF9tYW5hZ2VtZW50Ijp7ImlzX2VudGl0bGVkIjp0cnVlLCJpc190cmlhbCI6ZmFsc2V9LCJzdWJzY3JpcHRpb25zIjp7ImlzX2VudGl0bGVkIjp0cnVlLCJpc190cmlhbCI6ZmFsc2V9LCJzZXR0aW5ncyI6eyJpc19lbnRpdGxlZCI6dHJ1ZSwiaXNfdHJpYWwiOmZhbHNlfX0sImlkZW50aXR5Ijp7ImludGVybmFsIjp7ImF1dGhfdGltZSI6Nzk1LCJvcmdfaWQiOiIxMTAwOTEwMyJ9LCJhY2NvdW50X251bWJlciI6IjU5MTA1MzgiLCJhdXRoX3R5cGUiOiJiYXNpYy1hdXRoIiwidXNlciI6eyJpc19hY3RpdmUiOnRydWUsImxvY2FsZSI6ImVuX1VTIiwiaXNfb3JnX2FkbWluIjpmYWxzZSwidXNlcm5hbWUiOiJrd2Fsc2hAcmVkaGF0LmNvbSIsImVtYWlsIjoia3dhbHNoK3FhQHJlZGhhdC5jb20iLCJmaXJzdF9uYW1lIjoiS2VpdGgiLCJ1c2VyX2lkIjoiNTIyOTI0MzUiLCJsYXN0X25hbWUiOiJXYWxzaCIsImlzX2ludGVybmFsIjp0cnVlfSwidHlwZSI6IlVzZXIifX0='
# bundle = 'ansible'
# application = 'ansible-automation'
# c = CloudInfraClient()

# c.entitlements(identity_header)
# print(c.has_entitlements_access(identity_header, bundle))

# c.rbac_access(identity_header, application)
# print(c.has_rbac_access(identity_header, application))

class CloudInfraClient():
    def __init__(self):
        self.redis = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=os.environ.get('REDIS_PORT', 6379), db=os.environ.get('REDIS_DB', 0), password=os.environ.get('REDIS_PASSWORD'))

    def has_entitlements_access(self, identity_header, bundle):
        entitlements = self.entitlements(identity_header)
        return entitlements[bundle]['is_entitled']

    def entitlements(self, identity_header):
        user = self.user_obj(identity_header)
        key = f"user:{user['user_id']}:entitlements"
        user_cache = self.redis.get(key)

        if user_cache:
          entitlements = json.loads(user_cache)
          print('**** ENTITLEMENTS CACHE HIT IN CLIENT ****')
        else:
          print('**** ENTITLEMENTS CACHE MISS IN CLIENT ****')
          rsp = self.call_cache_service(identity_header, None, 'entitlements')
          entitlements = json.loads(rsp)

        self.output_ttl(key)
        return entitlements

    def has_rbac_access(self, identity_header, application, resource_type="*", verb="*"):
        access = self.rbac_access(identity_header, application)
        for a in access:
            if a["permission"] == f"{application}:{resource_type}:{verb}":
                return True

        return False

    def rbac_access(self, identity_header, application):
        user = self.user_obj(identity_header)
        key = f"user:{user['user_id']}:rbac"
        user_cache = self.redis.hget(key, application)

        if user_cache:
            access = json.loads(user_cache)
            print('**** RBAC CACHE HIT IN CLIENT ****')
        else:
            print('**** RBAC CACHE MISS IN CLIENT ****')
            rsp = self.call_cache_service(identity_header, application, 'rbac')
            access = json.loads(rsp)

        self.output_ttl(key)
        return access

    def user_obj(self, identity_header):
        return self.decoded_identity(identity_header)['identity']['user']

    def decoded_identity(self, identity_header):
        return json.loads(base64.b64decode(identity_header))

    def output_ttl(self, key):
        print(f'**** TTL: {self.redis.ttl(key)} ****')

    def call_cache_service(self, identity_header, application, cache_type):
        if cache_type == 'rbac':
            return requests.get(f'{os.environ.get("CACHE_HOST")}/api/platform-cache/cache/rbac?application={application}', headers={'x-rh-identity': identity_header}).text
        elif cache_type == 'entitlements':
            return requests.get(f'{os.environ.get("CACHE_HOST")}/api/platform-cache/cache/entitlements', headers={'x-rh-identity': identity_header}).text
