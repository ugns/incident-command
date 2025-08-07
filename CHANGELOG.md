# CHANGELOG

<!-- version list -->

## v1.5.10 (2025-08-07)

### Bug Fixes

- Increase timeout for JWKS URL request to improve reliability
  ([`c0f7005`](https://github.com/ugns/incident-command/commit/c0f7005927710a2ef3d7fe5d5f7f261734026cfd))


## v1.5.9 (2025-08-07)

### Bug Fixes

- Add aws-lambda-typing dependency for improved type safety
  ([`433ac50`](https://github.com/ugns/incident-command/commit/433ac50ec50ab06f8acbed73cc68c8e300a7652c))


## v1.5.8 (2025-08-07)

### Bug Fixes

- Set logging level for EventCoord.client.auth to match global LOG_LEVEL
  ([`8622bb7`](https://github.com/ugns/incident-command/commit/8622bb74d207fc30314cfad9c921ebda571fc302))


## v1.5.7 (2025-08-06)

### Bug Fixes

- Remove trailing slash from JWT issuer URL in auth_callback environment variables
  ([`b9325a4`](https://github.com/ugns/incident-command/commit/b9325a401dd06e2061574289767924343997c876))


## v1.5.6 (2025-08-06)

### Bug Fixes

- Add JKU header to JWT for JWKS URL in lambda_handler
  ([`40e2017`](https://github.com/ugns/incident-command/commit/40e2017e382b5358a08ad816be86b7c9984d6970))


## v1.5.5 (2025-08-06)

### Bug Fixes

- Update JWKS_URL to remove redundant auth path in WebSocket Lambda environment variables
  ([`586c379`](https://github.com/ugns/incident-command/commit/586c379affa46b2fd54a3cddc40a8e9de85056e9))


## v1.5.4 (2025-08-06)

### Bug Fixes

- Clean up build directory during the clean process in Makefile
  ([`ae1bf74`](https://github.com/ugns/incident-command/commit/ae1bf7427e98fc6d8ea1ed3580320b1e3caf00fc))

- Update JWT_ISSUER to include trailing slash and import JsonWebKey for key generation
  ([`30e774b`](https://github.com/ugns/incident-command/commit/30e774b99edc8a6a1f5d1f980fb2a92b87a9a798))


## v1.5.3 (2025-08-06)

### Bug Fixes

- Ensure cryptography dependency is included in the project dependencies
  ([`6c7a4f5`](https://github.com/ugns/incident-command/commit/6c7a4f5f55b310b60aee5f1291b0fb4a3f5b524b))


## v1.5.2 (2025-08-06)

### Bug Fixes

- Update Docker build process to use --no-cache-dir for pip installations
  ([`5f469bc`](https://github.com/ugns/incident-command/commit/5f469bc85b0810bdc9c120f716a1b781a0e021ed))


## v1.5.1 (2025-08-06)

### Bug Fixes

- Correct parent_id reference for /.well-known resource in API Gateway
  ([`0606702`](https://github.com/ugns/incident-command/commit/0606702fb696f68feb21b4020dba1a55d25b1e99))


## v1.5.0 (2025-08-06)

### Features

- Add JWT issuer environment variable and update JWKS URL paths
  ([`375ef3e`](https://github.com/ugns/incident-command/commit/375ef3ee3dc95775a4d8dc0b5302b6a02fe6d6fb))


## v1.4.2 (2025-08-06)

### Bug Fixes

- Remove installation of system dependencies from Terraform workflow
  ([`3c1350d`](https://github.com/ugns/incident-command/commit/3c1350db45d0b581e8b8a534265b8b8f89115322))


## v1.4.1 (2025-08-06)

### Bug Fixes

- Decode JWT token to UTF-8 before returning
  ([`81b4a1d`](https://github.com/ugns/incident-command/commit/81b4a1dace84336eedca104d6e92f79e42f9c146))


## v1.4.0 (2025-08-06)

### Features

- Add Lambda Secrets Manager policy for JWT key access
  ([`decd495`](https://github.com/ugns/incident-command/commit/decd495016e4988d74d9bdf09de728ba640faebc))


## v1.3.2 (2025-08-06)

### Bug Fixes

- Update artifact download path in Terraform workflow
  ([`bdac4a4`](https://github.com/ugns/incident-command/commit/bdac4a45a1a28d6a717aac7919d5aa244696d8aa))


## v1.3.1 (2025-08-06)

### Bug Fixes

- Update artifact download path in Terraform workflow
  ([`12ae232`](https://github.com/ugns/incident-command/commit/12ae232cfa73f88986cb74e5695567ab9eb980f4))


## v1.3.0 (2025-08-06)

### Features

- Implement EventCoord shared code with AWS integration and JWT verification
  ([`53d0fa6`](https://github.com/ugns/incident-command/commit/53d0fa678850a0e02e7fb00148bab32b950b7b3c))

- Update permissions for Terraform job to allow write access
  ([`cdde5e6`](https://github.com/ugns/incident-command/commit/cdde5e66eaf206af8997ea41f5fbb55207e5fdf5))


## v1.2.0 (2025-08-06)

### Features

- Add artifact upload steps for distribution and shared Lambda layer in Terraform workflow
  ([`c032d80`](https://github.com/ugns/incident-command/commit/c032d80743c48b7b93fde8173146beba943ef8b0))


## v1.1.0 (2025-08-06)

### Features

- Update Terraform workflow to upload JSON field files and modify Lambda environment variable for
  JWKS URL
  ([`2a6b34f`](https://github.com/ugns/incident-command/commit/2a6b34f56b55e9865ca9d426732331f6f222d0cf))


## v1.0.0 (2025-08-06)

- Initial Release
