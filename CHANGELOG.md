# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-04-14

### Added
- **Community Documentation** - Comprehensive contributing guidelines and development setup
- **Professional Sphinx Docs** - Complete documentation with Furo theme, autodoc, and search

### Documentation Structure
- Getting Started (Installation, Quickstart, Configuration)
- API Reference (Connection, Repository, QueryBuilder, Exceptions)
- Tutorials (CRUD, Pagination, Transactions, Bulk Operations, Async)
- Community & Contributing

## [1.2.0] - 2026-04-13

### Added
- **90%+ Test Coverage** - Comprehensive test suite with 263 unit tests
- **Async Connection Pool** - `AsyncConnectionPool` for high-performance async operations
- **Advanced Query Builder** - Full support for JOINs, GROUP BY, HAVING, UNION
- **Migration System** - Version-based schema migration with rollback support
- **Type Validators** - Comprehensive type validation and serialization
- **Exception Hierarchy** - 12 custom exception types for precise error handling
- **Stress Testing Suite** - Built-in stress tests for concurrent operations
- **Benchmark Suite** - Comparative benchmarks vs sqlite3, sqlalchemy, aiosqlite

### Fixed
- **aiosqlite Thread Safety** - Fixed connection threading issues in async methods
- **Test Isolation** - All tests now use independent database files (no shared state)
- **Pool Connection Management** - Proper cleanup and health checks
- **Transaction Rollback** - Correct error handling in transactions

### Changed
- **Connection Pool** - Enhanced with WAL mode enabled by default
- **Async Methods** - Improved connection lifecycle management
- **Repository** - Better integration with connection pool

### Performance
- **Connection Pooling** - Thread-safe with minimal lock contention
- **WAL Mode** - Enabled by default for concurrent read/write
- **Memory Optimization** - Connection recycling and health checks

## [1.1.0] - 2024

### Added
- Connection Pooling
- Advanced Query Builder
- Schema migrations
- Stress testing
- Benchmarking tools

## [1.0.0] - 2024

### Added
- Initial stable release
- Basic CRUD operations
- Pydantic model integration
- Table synchronization
- Query builder

---

## [Unreleased] - yyyy-mm-dd

### Added
- (Future features here)

### Changed
- (Changes here)

### Deprecated
- (Soon-to-be removed features)

### Removed
- (Removed features)

### Fixed
- (Bug fixes)

### Security
- (Security improvements)
