# DoRéMix documentation

This folder centralizes the project-level technical documentation.

## Contents

- [Architecture overview](architecture/overview.md)
- [Database schema reference](database/schema-reference.md)

## Scope

These documents describe:

- the global application architecture,
- the main runtime components,
- the backend API conventions,
- the folder organization,
- the PostgreSQL data model and its relationships,
- the main request and data flows between the frontend, CLI, backend, and database.

## Source of truth

The documentation is based on the current implementation in:

- [src/back](../src/back)
- [src/front](../src/front)
- [src/cli](../src/cli)
- [build/database/init.sql](../build/database/init.sql)
- [docker-compose.yml](../docker-compose.yml)
