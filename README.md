# 0. Introduction

This file describes the proposed solution for the Rindus coding task assignment.

Due to lack of time, the Docker container hasn't been implemented, so the service must be run with the django development server instead.

The first time the project is run, the database migrations must be done with:

`python3 manage.py makemigrations`
`python3 manage.py migrate`

And after that run the development server with:

`python3 manage.py runserver`

Since the service will run without a container, the database used has been the built in SQLite instead of the requested Postgres one.

# 1. Django command to import placeholder data

To import the data from the placeholder, execute:

`python3 manage.py import_placeholder_data`

This command will download the posts and comments from https://jsonplaceholder.typicode.com/ and will save it to the local Postgres database. The data models used to store in the database can be found in `rindus_ct/res_api/models.py`

This command requires an empty database to work. If the database is not empty, it will return an error message to prevent the loss of modifications.

However it is possible to delete all database data with the command:

`python3 manage.py clear_data`

After executing it, the fresh data can be imported again.


# 2. REST API to manage the data

## 2.1 API documentation

For API documentation, I have used the package drf-spectacular that uses Swagger and OpenAPI to generate interactive documentation automatically from the code. To install this package, run:

`pip install drf-spectacular`

To visualize the generated documentation, please run the development server and access it at:

`http://127.0.0.1:8000/docs/`

At that page, you can look up all available requests and methods, the expected response codes and the schemas needed for requests and responses.

## 2.2 Authorization and authentication

The requests are protected by token authorization and authentication. So, in order to test the API manually, it is necessary to create users manually in the Django admin site and generate tokens to use in the requests. For doing it, follow this steps:

Create a superuser with the command:

`python3 manage.py createsuperuser`

Go to the admin site at: http://127.0.0.1:8000/admin/ and log in with the superuser created

Add a token in the Auth Token section.

Go to the Swagger doc page http://127.0.0.1:8000/docs/ and authorize the requests in the upper right corner of the screen with the previous token and the prefix "Token " appended before it.

Now the requests can be manually tested in the Swagger web interface.

# 3. System synchronization

Since the system developed acts as master, it means that the data in the local database must be preserved, compared to the data in the remote placeholder, and the system must send the appropiate REST commands to the remote placeholder to change its data.

The remote placeholder schemas do not have any time information about when the last changes were done (it does not have any "last modified" field). For this reason, it is not possible to attempt an incremental synchronization based on the latest changes.

It is necessary then to do a whole synchronization between datasets. The whole remote dataset is downloaded, compared to the data in the database, and the changes are sent back to the placehodler.

Please note that this approach is less efficient than a incremental time based one, but no other option is possible if there is no time reference available.

The synchronization is triggered running the django command:

`python3 manage.py synchronize`


# 4. Testing

# 4.1 Testing manually

The API can be tested manually through CLI curl commands, or through the Swagger browsable API as it has been described in the previous sections.

# 4.2 Automated tests

A test suite is included in rindus_ct/rest_api/tests. To execute the tests, run:

`python3 manage.py test`


# 5. Pending improvements

Due to lack of time, there are quite a few things that need to be improved but haven't been completed due to lack of time. The most important are:

- Delivery with docker and docker compose
- Add asynchronous support to requests to improve system performance (asyncio functionality)
- Add OpenAPI schemas to DRF views to generate automatic Swagger documentation for the responses with all response codes in the docs


