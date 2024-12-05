#### This project was developed as a collaborative effort by myself and 5 other students for a university module.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before installing the software, you need to have the following:

- [Python 3 or higher](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
### Installing

#### 1. Clone the Repository

```bash
git clone https://github.com/FathanRaedaya/router.git
cd router
```

#### 2. Install the Dependencies

```bash
pip3 install -r requirements.txt
```

#### 3. Set the Flask App

For Windows:
```bash
set FLASK_APP={path_to_app)\__init__.py
```

For Unix based OS:
```bash
export FLASK_APP={path_to_app)/__init__.py
```
#### 4. Run Flask

```bash
flask run
```

To run in debug mode:
```bash
flask run --debug
```

