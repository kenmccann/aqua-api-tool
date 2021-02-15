<img src="https://avatars3.githubusercontent.com/u/12783832?s=200&v=4" height="100" width="100" />

# aqua-api-tool

The Aqua API Tool is a simple utility for interacting with your Aqua Enterprise
API in order to perform useful tasks not (yet) easily achieved in the Aqua UI. 
This tool can also be used in an automated fashion to quickly make changes to 
your Aqua Enterprise Environment in a CI/CD pipeline.

## Usage

This utility is intended to be run within a container, but you can easily run
the aqua-api-tool.py python script directly.  You'll just need to `pip install
requests` into your python runtime environment. 

### Run as a container
The official lightweight Linux image, based on Alpine, is hosted on Docker Hub
and you can find more information on 
[the Docker Hub page](https://hub.docker.com/repository/docker/kenmac/aqua-api-tool).

### Pull the Docker image
```bash
$ docker pull kenmac/aqua-api-tool:latest
```

#### List all images containing sensitive files
```bash
$ docker run --rm kenmac/aqua-api-tool:latest --show-sensitive-images -u <user> -p <password> --url https://aqua.hostname.com
```

#### Delete all empty repositories in Aqua
```bash
$ docker run --rm kenmac/aqua-api-tool:latest --delete-empty-repositories -u <user> -p <password> --url https://aqua.hostname.com
```

#### Delete *all* repositories in Aqua
```bash
$ docker run --rm kenmac/aqua-api-tool:latest --delete-all-repositories -u <user> -p <password> --url https://aqua.hostname.com
```

#### Clear all items in the 'Pending' scan queue
```bash
$ docker run --rm kenmac/aqua-api-tool:latest --clear-pending-queue -u <user> -p <password> --url https://aqua.hostname.com
```

You can always see the full usage using the `-h` parameter:
```
$ docker run --rm kenmac/aqua-api-tool:latest -h 
usage: aqua-api-tool.py [-h] -u USER -p PASSWORD -U URL [-s] [-cp] [-dr] [-de]
                        [--auth-header AUTH_HEADER]

Aqua Security tool for interacting with Aqua Enterprise API.

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Username or service account for logging into Aqua.
  -p PASSWORD, --password PASSWORD
                        Password for logging into Aqua.
  -U URL, --url URL     Aqua base URL. (ie. https://aqua.company.com)
  -s, --show-sensitive-images
                        Return all known images that contain sensitive data.
  -cp, --clear-pending-queue
                        Clear all items in the pending scan queue.
  -dr, --delete-all-repositories
                        Delete all known image repositories. Warning: this
                        action cannot be undone and all image data will be
                        deleted.
  -de, --delete-empty-repositories
                        Delete all empty image repositories. Warning: this
                        action cannot be undone and all image data will be
                        deleted.
  --auth-header AUTH_HEADER
                        If you use a custom authorization header for API
                        requests, specify with this parameter. (See Aqua docs
                        regarding "AUTHORIZATION_HEADER")
```

### Authorization Headers
If your Aqua Enterprise installation has a customized authorization header, often used with reverse proxies, you can 
specify this custom header with `--auth-header <header value>`.
```bash
$ docker run --rm kenmac/aqua-api-tool:latest --auth-header aqua-auth ....
```