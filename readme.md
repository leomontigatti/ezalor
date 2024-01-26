# Ezalor

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

Ezalor is a Django web application designed to gather news from a set of pages, manage and publish them on different Facebook and Instagram pages.

## Installation

Create the folder that will hold the app files and enter it.

``` bash
mkdir ezalor
cd ezalor/
```

Copy and paste to clone the project repository.

``` bash
git clone https://github.com/leomontigatti/ezalor.git
```

Some of the libraries used by the app depend on other ones to work properly. We will install all of them just in case anyone is missing.

``` bash
sudo apt update
sudo apt install python3-dev virtualenv redis-server
```

It's recommended to install app-only related dependencies inside a virtual environment. For this we will use *virtualenv* installed previously.

``` bash
virtualenv venv
```

Activate the virtual environment and install the those dependencies.

``` bash
source venv/bin/activate
pip install -r requirements.txt
```

> [!IMPORTANT]
> From now on, some **environment variables** are needed in order to run the app. Please contact me and I will provide them.

## Usage

Run migrations and, for functionality reasons, create the first superuser with the credentials you prefer.

``` bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

Run the web server using:

``` bash
python3 manage.py runserver
```

> [!TIP]
> You should now be able to open your web browser, navigate to [localhost](http://127.0.0.1:8000/) and start using the app.
