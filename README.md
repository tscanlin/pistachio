S3 stored Credential loader module.
================
Copyright Optimizely, Inc., All Rights Reserved.

The `pistachio` module exists to load credentials stored on S3.

## Quickstart
Put a `pistachio.yaml` file in your project repo with the following content:
```
bucket: YOURBUCKETHERE
```
Put another `pistachio.yaml` file in your home directory with the following content:
```
key: YOURAWSKEY
secret: YOURAWSKEYSECRET
```

## Accessing CONFIG
One only needs to import this module to load the configs.

```
import pistachio
value = pistachio.CONFIG['some_key']
```

#### Under the Hood
When you run `import pistachio` it:  
- Checks if you have a 'cache' setting
  - If so, attepmpts to load from the cache file, if it exists
- Otherwise, loads the config by merging yaml files from specified bucket/folders
  - This can be slow, as it has to download each file from S3 over the network
- If 'cache' is set, saves the cache
- Saves the loaded config to `pistachio.CONFIG`

Calling `pistachio.CONFIG` is quick after the intial import, as it's just a hash constant

## Settings
This is loaded from files named `pistachio.yaml`.  
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
##### 3. Lastly the `pistachio.yaml` from your $HOME directory if one exists
This is a good place to set your personal AWS keys
#### Format of `pistachio.yaml` files
```
key: STRING 
# REQUIRED
# Key used to access the Amazon API
```
```
secret: STRING 
# REQUIRED
# Secret Key used to access the Amazon API
```
```
bucket: STRING 
# REQUIRED
# Bucket to load Configs from.
```
```
path: STRING/ARRAY
# OPTIONAL
# Folder(s) within the bucket to load from.
# Can be string or array.  
# When an array, folders listed first have higher precedence.  
# When unset, looks in the root of the bucket.
```
```
cache: STRING 
# OPTIONAL
# Path, relative to the pistachio.yaml file, to save/load cache from
# When unset, does not attempt to load from cache, or save from cache.
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
cache: ./pistachio.cache
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
