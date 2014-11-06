S3 stored Credential loader module.
================
Copyright Optimizely, Inc., All Rights Reserved.

The `pistachio` module exists to load credentials stored on S3.

## Settings
This is loaded from a file called `pistachio.yaml`. It loads the first file starting from the current directory and traverses upwards, meaning, any parent folder can also contain this file.

```
key: STRING (REQUIRED/ENV_LOADABLE* See below)
# Key used to access the Amazon API
```
```
secret: STRING (REQUIRED/ENV_LOADABLE* See below)
# Secret Key used to access the Amazon API
```
```
bucket: STRING (REQUIRED)
# Bucket to load Configs from.
```
```
path: STRING/ARRAY (OPTIONAL)
# Folder(s) within the bucket to load from.
# Can be string or array.  
# When an array, folders listed first have higher precedence.  
# When unset, looks in the root of the bucket.
```
```
cache: STRING (OPTIONAL)
# Path, relative to the pistachio.yaml file, to save/load cache from
# When unset, does not attempt to load from cache, or save from cache.
```

\* If the `pistachio.yaml` file does not contain a key and secret, it will check check the following evironment variables for them, respectively: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

#### Examples
```
AWS_ACCESS_KEY_ID=K4JD1H
AWS_SECRET_ACCESS_KEY=HF82E3DF234X

bucket: optimizely-pistachio-dev
path:   www
```
```
key:    K4JD1H
secret: HF82E3DF234X
bucket: optimizely-pistachio-prod
path:
  - www
  - common
cache: ./pistachi.cache
```
## Accessing CONFIGS
One only needs to import this module to load the configs.

```
import pistachio
value = pistachio.CONFIG['some_key']
```

## Uploading Credentials
Credentials should be uploaded to the respective bucket, and optionally folder, that you are setting pistachio to load from. All files within the specified bucket/folder(s) ending in .yaml will be merged together in alphabetical order.

Example:
```
MyBucket/
  common/
    jenkins.yaml
    github.yaml
  frontend/
    highcharts.yaml
  backend/
    aws.yaml
```    
