# CHANGELOG

<!-- version list -->

## v1.22.1 (2025-08-15)

### Bug Fixes

- Work to correct format of openapi_config
  ([`82a953c`](https://github.com/ugns/incident-command/commit/82a953cc4b95233efd2a34fc5b3270eb4b93dada))


## v1.22.0 (2025-08-15)

### Features

- Add concurrency settings to Terraform job in GitHub Actions workflow
  ([`201e0b1`](https://github.com/ugns/incident-command/commit/201e0b152e51de09e5f2467c69a04bbfc93382e2))


## v1.21.0 (2025-08-14)

### Features

- Update GitHub Actions workflow to restrict job execution to push events on main branch
  ([`8233c10`](https://github.com/ugns/incident-command/commit/8233c100020cb29b1cf5307a5e2f16344027d07d))


## v1.20.0 (2025-08-14)

### Features

- Update GitHub Actions workflow to ensure proper job dependencies and execution conditions
  ([`952a423`](https://github.com/ugns/incident-command/commit/952a423b18c128cb44928693a3653c6d82a7faa7))


## v1.19.0 (2025-08-14)

### Features

- Refactor Lambda function configurations to use archive_file data sources for improved
  maintainability
  ([`73ea3d7`](https://github.com/ugns/incident-command/commit/73ea3d7812a56487a305c5e41449a9d18417d112))


## v1.18.0 (2025-08-14)

### Features

- Update notify_ws_stream Lambda function to use specific handler file path
  ([`fe67703`](https://github.com/ugns/incident-command/commit/fe677037857001dc2678c33209d9f660dd543b95))


## v1.17.0 (2025-08-14)

### Features

- Update Lambda function configurations to use specific handler files and remove unused archive_file
  resources
  ([`b0123cf`](https://github.com/ugns/incident-command/commit/b0123cfce91b238f54fbc4927f06ed49bf6b717f))


## v1.16.0 (2025-08-13)

### Features

- Consolidate API Gateway integration responses into local variables for improved organization
  ([`ecef73c`](https://github.com/ugns/incident-command/commit/ecef73c50cc65562452da95f80bfe014ffac0118))


## v1.15.0 (2025-08-13)

### Features

- Allow access to all indexes of ws_connections DynamoDB table in IAM policy
  ([`c3758d9`](https://github.com/ugns/incident-command/commit/c3758d9946e4868e92fc4af976bfe7196991a6f8))


## v1.14.0 (2025-08-13)

### Features

- Update WebSocket disconnect handler to use DynamoDB query for connection retrieval and enhance
  error logging
  ([`6186a7b`](https://github.com/ugns/incident-command/commit/6186a7bf8dc078986528bc76522d5112fd6f3bdd))


## v1.13.0 (2025-08-13)

### Bug Fixes

- Change LOG_LEVEL from DEBUG to INFO in Lambda functions for improved logging clarity
  ([`6620cf3`](https://github.com/ugns/incident-command/commit/6620cf3225910441bb67ce156485c1844c467dc3))

### Features

- Add APIGatewayProxyEventV2 import and update user identifier handling in ws_connect lambda
  ([`9920170`](https://github.com/ugns/incident-command/commit/9920170c2f8c104f21957b19a4268f2098573f79))

- Integrate AWS X-Ray SDK for enhanced tracing across Lambda functions
  ([`d575d6a`](https://github.com/ugns/incident-command/commit/d575d6ad49f21a15c34902a038bb1fa328df261e))


## v1.12.1 (2025-08-13)

### Bug Fixes

- Correct eventSourceArn to eventSourceARN in lambda_handler logging
  ([`aec5be8`](https://github.com/ugns/incident-command/commit/aec5be804c2b90a4b06bd25c0c14f9a0880221e3))


## v1.12.0 (2025-08-13)

### Features

- Add logging for missing eventSourceArn in lambda_handler
  ([`5e6e0c9`](https://github.com/ugns/incident-command/commit/5e6e0c91bfeae0e7b8e700bc83071247130fbe3c))


## v1.11.0 (2025-08-13)

### Features

- Update Lambda function names to include EventCoord prefix for clarity
  ([`1b89c3d`](https://github.com/ugns/incident-command/commit/1b89c3db6168a14dd85535f75f449a0f861ee596))


## v1.10.0 (2025-08-13)

### Features

- Enhance JWT verification with improved error handling and audience validation
  ([`4e8941c`](https://github.com/ugns/incident-command/commit/4e8941c0ff97950c31578677c77abdd226d9ae19))


## v1.9.0 (2025-08-08)

### Features

- Add CORS headers and JSON parsing to API Gateway response in handler.py
  ([`692f834`](https://github.com/ugns/incident-command/commit/692f834367581e0ff93d8b623f48ef99a60c2b81))


## v1.8.0 (2025-08-07)

### Features

- Set timeout and add shared layer to WebSocket Lambda functions
  ([`643581e`](https://github.com/ugns/incident-command/commit/643581ef95e57fa572f1e8cb9bfe39a9e9609444))


## v1.7.0 (2025-08-07)

### Features

- Set timeout for multiple Lambda functions to 10 seconds
  ([`c6fd4ce`](https://github.com/ugns/incident-command/commit/c6fd4ced658737e0fb3e8ad36eebb2ef89657123))


## v1.6.0 (2025-08-07)

### Features

- Add shared layer to OpenAPI Lambda function
  ([`6e8bd3b`](https://github.com/ugns/incident-command/commit/6e8bd3bb3daaef165e3f66b46b5d3b4061eab642))


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
