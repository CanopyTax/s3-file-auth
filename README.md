# s3-file-auth
Require github auth for viewing your s3 files

This application wraps s3 and allows you to serve s3 files only to those 
who are part of your github org. The paths to the files are the same as s3.

This will only wrap one bucket, so if you want multiple buckets, you will have
to run multiple of there (or you could fork this and have it support multiple)

In order to get this to work you need to first register a github application.
The callback url is `https://[hostname]/oauth_callback/github`. 
For example, if you were running this on localhost, you could set the callback
to `http://localhost:8080/oauth_callback/github`

In order to go to your file {bucket}{key} you would simply go to `/key`. 
Everything that doesnt exist in s3 will return a 404. Paths much match the key
exactly.

## just get me running

```
docker run -p 8080:8080 -e S3_BUCKET=mybucket -e GITHUB_ID=myclientid -e GITHUB_SECRET=mysecret -e GITHUB_ORG=myorg canopytax/s3-file-auth
```

## Configuration options

The following environment variables exist for configuration

```
S3_BUCKET  # required
GITHUB_ID  # required
GITHUB_SECRET  # required
GITHUB_ORG  # required
COOKIE_NAME  # default is s3githubauth
COOKIE_KEY  # default is randomly generated
```

You should set the `COOKIE_KEY` if you want to be able to share the cookie with
 other services/instances. If you do not set `COOKIE_KEY` and you have more than
 one server, you will have problems, dont say I didnt warn you.

`COOKIE_KEY` should be a 16 character string

If you dont use an aws instance profile, you will also need to provide the AWS
key and secret through environment variables.