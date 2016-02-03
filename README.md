S3 stored Credential loader module.
================
[![Build Status](https://travis-ci.org/optimizely/pistachio.svg?branch=master)](https://travis-ci.org/optimizely/pistachio)

Copyright Optimizely, Inc., All Rights Reserved.

The `pistachio` module exists to load credentials stored on S3. 
This package works in conjunction with [boto3](https://github.com/boto/boto3) to link your AWS credentials 
and seamlessly connect you to your Amazon S3 bucket.  
This package understands nothing about how your S3 security is managed.  
This package assumes it has access to the S3 bucket/folder(s) you set it to use.

## Quickstart

#### Setup
Put a `pistachio.yaml` or `.pistachio` file in your project repo with the following content:
```
bucket: <S3_bucket_name>
```
Add `pistachio.cache` to your `.gitignore`, so you don't track cache files.

#### Accessing the loaded config
```
import pistachio

config = pistachio.load()
print config  # Print the results

value = config[<some key>]  # Access a value
```

#### Under the Hood
When you run `pistachio.load()` it:  
- Checks if you have a 'cache' setting
  - If so, checks that `path` setting matches Pistachio's `path` value in the cache file, if it exists
  - If so, attempts to load from the cache file, if it exists
- Otherwise, loads the config by merging yaml files from specified bucket/folders
  - This can be slow, as it has to download each file from S3 over the network
- If 'cache' is set, saves the cache
- Saves the loaded config to `pistachio.CONFIG`

## Settings
This is loaded from files named `pistachio.yaml` and `.pistachio`.  
Keys set in higher priority files receive precedence and override lower priority files.

#### Load priority from highest to lowest:

##### 1. Environment variables prefixed with `PISTACHIO_`

`export PISTACHIO_<SOME KEY>=<SOME VALUE>` would override any keys set in the `pistachio.yaml` or `.pistachio` files

##### 2. The `pistachio.yaml` or `.pistachio` files starting from the current working directory, up to the root of the filesystem.

```
./src/www/pistachio.yaml # Would Override...
./src/pistachio.yaml # Which Would Override...
./pistachio.yaml # 
```

##### 3. Lastly the `pistachio.yaml` or `.pistachio` from your $HOME directory if one exists

This is a good place to set your global pistachio configs

#### Format of `pistachio.yaml`/`.pistachio` files

```
bucket: STRING
# REQUIRED
# Bucket to load Configs from.
```
```
profile: STRING 
# OPTIONAL
# DEFAULT: 'default'
# AWS Profile containing your key and secret
```
```
parallel: STRING
# OPTIONAL
# DEFAULT: 'false'
# When set to 'true', s3 downloads run in parallel
```
```
path: STRING/LIST
# OPTIONAL
# DEFAULT: ['']  # All contents of bucket
# Folder(s) within the bucket to load from.
# Can be string or array.  
# When an array, folders listed first have higher precedence.
# When setting through ENV variable, folders are ':' delimited. E.g. `PISTACHIO_PATH=folder1:folder2`
# When unset, looks in the root of the bucket.
```
```
cache: HASH
# OPTIONAL
# DEFAULT: {}
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

#### Example pistachio.yaml or .pistachio file
```

# pistachio.yaml
bucket: MyBucket
path:   www
```

#### Example environment variables
```
$ export PISTACHIO_PROFILE=default
$ export PISTACHIO_BUCKET=MyBucket
$ export PISTACHIO_PATH=www:common
```

#### Example pistachio.yaml or .pistachio file with extra configurations
```
# pistachio.yaml
profile: default
bucket: MyBucket
path:
  - www
  - common
cache: 
  path: ./pistachio.cache
  expires: 60  # minutes
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
