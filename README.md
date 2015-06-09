S3 stored Credential loader module.
================
[![Build Status](https://travis-ci.org/optimizely/pistachio.svg?branch=master)](https://travis-ci.org/optimizely/pistachio)

Copyright Optimizely, Inc., All Rights Reserved.

The `pistachio` module exists to load credentials stored on S3.  
This package understands nothing about how your S3 security is managed.  
This package assumes it has access to the S3 bucket/folder(s) you set it to use.

## Quickstart
Put a `pistachio.yaml` file in your project repo with the following content:
```
bucket: YOURBUCKETHERE
```
Put another `.pistachio` file in your home directory with the following content:
```
key: YOURAWSKEY
secret: YOURAWSKEYSECRET
```
Add `pistachio.cache` to your `.gitignore`, so you don't track cache files.

## Accessing the loaded config
```
import pistachio
config = pistachio.load()
value = config['some_key']
```

#### Under the Hood
When you run `pistachio.load()` it:  
- Checks if you have a 'cache' setting
  - If so, attepmpts to load from the cache file, if it exists
- Otherwise, loads the config by merging yaml files from specified bucket/folders
  - This can be slow, as it has to download each file from S3 over the network
- If 'cache' is set, saves the cache
- Saves the loaded config to `pistachio.CONFIG`

## Settings
This is loaded from files named `pistachio.yaml` and `.pistachio`.  
Only `.pistachio` files can contain keys/secrets
Keys set in higher priority files receive precedence and override lower priority files.
#### Load priority from highest to lowest:  
##### 1. Environment variables prefixed with `PISTACHIO_`
`export PISTACHIO_KEY=YOURKEYHERE` would override any keys set in the `pistachio.yaml` files  
##### 2. The `pistachio.yaml` files starting from the current working directory, up to the root of the filesystem.
```
./src/www/pistachio.yaml # Would Override...
./src/pistachio.yaml # Which Would Override...
./pistachio.yaml # 
```  
##### 3. Lastly the `pistachio.yaml` or `.pistachio` from your $HOME directory if one exists
This is a good place to set your personal AWS keys
#### Format of `pistachio.yaml`/`.pistachio` files
```
key: STRING 
# REQUIRED
# Key used to access the Amazon API
# Can only be placed in .pistachio files
```
```
secret: STRING 
# REQUIRED
# Secret Key used to access the Amazon API
# Can only be placed in .pistachio files
```
```
bucket: STRING
# REQUIRED
# Bucket to load Configs from.
```
```
skipauth: STRING
# OPTIONAL
# When set to 'true', the key & secret aren't used when creating the s3 connection
```
```
path: STRING/ARRAY
# OPTIONAL
# Folder(s) within the bucket to load from.
# Can be string or array.  
# When an array, folders listed first have higher precedence.
# When setting through ENV variable, folders are ':' delimited. E.g. `PISTACHIO_PATH=prod:dev`
# When unset, looks in the root of the bucket.
```
```
cache: HASH
# OPTIONAL
# When unset, does not attempt to load from cache, or save from cache.
 path: STRING
 # REQUIRED
 # Not required if no cache hash is set
 # Relative to the pistachio.yaml file, to save/load cache from
 expires: INT
 # OPTIONAL
 # Time in minutes until cache will expire
 # When unset, cache will not expire
 enabled: BOOLEAN
 # OPTIONAL
 # DEFAULT: True
 # When False, will disable cache
```

#### Example pistachio.yaml files
```
# Example where Key/Secret is loaded into environment variables
# export PISTACHIO_KEY=K4JD1H
# export PISTACHIO_SECRET=HF82E3DF234X

# pistachio.yaml
bucket: optimizely-pistachio-dev
path:   www
```
```
# pistachio.yaml
key:    K4JD1H
secret: HF82E3DF234X
bucket: optimizely-pistachio-prod
path:
  - www
  - common
cache: 
  path: ./pistachio.cache
  expires: 60 # minutes
```

## Storing Credentials
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

## Running tests
All tests are in the test/ directory. To run them do the following:

```
python -m test
```
