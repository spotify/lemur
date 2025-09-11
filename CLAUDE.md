# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lemur is a TLS certificate management and orchestration service developed by Netflix. It acts as a broker between Certificate Authorities (CAs) and environments, providing a central portal for developers to issue TLS certificates with secure defaults. The project is built with Python Flask backend and AngularJS frontend.

## Development Commands

### Setup and Installation
- `make develop` - Full development setup (installs npm dependencies, pip packages, builds static assets)
- `make release` - Production build without dev dependencies
- `npm install` - Install Node.js dependencies
- `pip install -e .` - Install Lemur package in development mode

### Database
- `make reset-db` - Drop and recreate the PostgreSQL 'lemur' database with migrations
- `lemur db upgrade` - Apply database migrations

### Testing
- `make test` - Run all tests (Python + linting)
- `make test-python` - Run Python tests with coverage
- `coverage run --source lemur -m py.test` - Run tests with coverage
- `make test-js` - Run JavaScript tests (`npm test`)
- `make test-cli` - Test CLI functionality

### Linting
- `make lint` - Run all linting (Python + JavaScript)
- `make lint-python` - Run Python linting (`flake8 lemur`)
- `make lint-js` - Run JavaScript linting (`npm run lint`)

### Static Assets
- `gulp build` - Build static assets
- `gulp package` - Package static assets
- `node_modules/.bin/gulp clean` - Clean static cache

### Requirements Management
- `make up-reqs` - Update all requirements files using pip-tools
- **IMPORTANT**: All Python dependencies are managed via requirements*.in files. Use `make up-reqs` to regenerate requirements*.txt files
- Do NOT manually edit requirements.txt files - they are auto-generated

## Architecture

### Core Components
- **Backend**: Python Flask application with SQLAlchemy ORM
- **Frontend**: AngularJS SPA with Gulp build system
- **Database**: PostgreSQL with pg_trgm extension
- **Plugin System**: Extensible plugin architecture for CAs, destinations, and notifications

### Key Directories
- `lemur/` - Main Python package containing all backend logic
- `lemur/plugins/` - Plugin implementations for various CAs and services
- `lemur/static/` - Frontend AngularJS application
- `lemur/migrations/` - Database migration files
- `lemur/tests/` - Test suite
- `docs/` - Documentation
- `docker/` - Docker configuration

### Plugin Architecture
Lemur uses an extensive plugin system with entry points defined in setup.py:
- **Issuers**: Certificate authorities (ACME, DigiCert, Verisign, etc.)
- **Destinations**: Certificate deployment targets (AWS, Kubernetes, SFTP, etc.)
- **Sources**: Certificate discovery and import (AWS, DigiCert, etc.)
- **Notifications**: Alert systems (Email, Slack, SNS)
- **Exporters**: Certificate format conversion (JKS, OpenSSL, CSR)

### Database Models
Core entities include certificates, authorities, destinations, domains, users, and roles with complex relationships managed through SQLAlchemy.

## Requirements
- Python 3.13+ (updated from 3.7+ for current compatibility)
- PostgreSQL with pg_trgm extension
- Node.js 18+ for frontend build system
- Redis (for some plugins)

## Recent Updates & Compatibility Notes

### Python 3.13 Compatibility
- Updated all dependencies to Python 3.13 compatible versions
- Fixed `importlib.metadata.entry_points()` API usage in `lemur/factory.py` (line 261)
- Updated Cloudflare package import in `lemur/plugins/lemur_acme/cloudflare.py`

### Node.js & Frontend Updates
- Updated `gulp-minify-css` to `gulp-clean-css` for Node.js v24 compatibility
- Fixed deprecated Node.js API usage in frontend build system
- All frontend builds now work with modern Node.js versions

### Dependency Management Process
1. Edit requirements*.in files to add/remove/update package constraints
2. Run `make up-reqs` to regenerate all requirements*.txt files using pip-compile
3. The up-reqs target updates: requirements.txt, requirements-tests.txt, requirements-dev.txt, requirements-docs.txt
4. Always use the virtual environment when running `make up-reqs`

## Configuration
- Main config in `lemur/default.conf.py`
- Test config in `lemur/tests/conf.py` (useful for development testing)
- Docker config in `docker/src/lemur.conf.py`
- Frontend build config in `gulpfile.js`

## Development Environment Setup

### Quick Start
1. Create Python virtual environment: `python3.13 -m venv venv`
2. Activate virtual environment: `source venv/bin/activate`
3. Run full development setup: `make develop`
4. This will install all dependencies, build frontend assets, and set up the development environment

### Troubleshooting Common Issues

#### Dependency Conflicts
- If you encounter dependency version conflicts, use `make up-reqs` to regenerate requirements files
- Common conflicts occur when switching Python versions or after merging changes
- Always activate the virtual environment before running `make up-reqs`

#### Frontend Build Issues
- If Node.js build fails, ensure you're using Node.js 18+ 
- Remove `node_modules` and `package-lock.json`, then run `npm install`
- The `gulp-clean-css` package replaced the deprecated `gulp-minify-css`

#### Application Import Issues
- For testing imports, use the test config: `LEMUR_CONF=/path/to/lemur/tests/conf.py`
- The test config provides minimal settings needed for basic functionality

### Testing Strategy
- Linting tests (`make lint`) should always pass
- Python unit tests may require database setup for full functionality
- JavaScript tests can run without backend dependencies
- Use `make test-js` and `make lint` for quick validation during development

## Spotify-Specific Features

This fork includes additional Spotify-specific enhancements:
- Enhanced task retry logic with Redis locks for race condition prevention
- Password login restrictions with configurable allow/deny lists
- Improved certificate renewal workflow with automatic retries
- Redis-based distributed locking for endpoint operations