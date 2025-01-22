<p align="center"><h1 align="center">ASYNCMONGO</h1></p>
<p align="center">
	<em>Asynchronous MongoDB Made Easy</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/Roshan-R/asyncmongo?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/Roshan-R/asyncmongo?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/Roshan-R/asyncmongo?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/Roshan-R/asyncmongo?style=default&color=0080ff" alt="repo-language-count">
</p>


##  Overview

asyncmongo is a Python library for working with MongoDB asynchronously. I’m building this project to learn more about how database drivers work and to explore what goes into creating one. It’s a mix of learning and coding, so things might evolve as I figure things out!

---


##  Getting Started

###  Prerequisites

Before getting started with asyncmongo, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Poetry


###  Installation

Install asyncmongo using one of the following methods:

**Build from source:**

1. Clone the asyncmongo repository:
```sh
❯ git clone https://github.com/Roshan-R/asyncmongo
```

2. Navigate to the project directory:
```sh
❯ cd asyncmongo
```

3. Install the project dependencies:


**Using `poetry`** &nbsp; [<img align="center" src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" />](https://python-poetry.org/)

```sh
❯ poetry install
```



###  Testing
Run the test suite using the following command:
**Using `poetry`** &nbsp; [<img align="center" src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" />](https://python-poetry.org/)

```sh
❯ poetry run pytest
```


---
##  Project Roadmap

### Currently Supported Operations
- `find`
- `find_one`
- `insert_one`
- `bulk_insert`
- `aggregate`

- [X] **`Basic Connection`**: <strike>Set up a basic connection to a MongoDB instance.</strike>
- [ ] **`Authentication`**:  
	- [X] Added support for SCRAM-SHA-256 authentication scheme.  
	- [ ] Add support for additional authentication mechanisms (e.g LDAP).  
- [ ] **`Connection Pooling`**: Develop connection pooling for better performance and scalability.
- [ ] **`Testing and Benchmarks`**: Write unit tests and benchmarks.
	- [ ] 	Write unit tests for connection handling and CRUD operations.
	- [ ] 	Create benchmarks to measure and optimize performance.
- [ ] **`Cython`**: Rewrite core components in Cython to improve performance, inspired by asyncpg's implementation.
---


##  License

This project is protected under the MIT License. 
