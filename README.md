# 1. Introduction

This file describes the proposed solution for the Rindus coding task assignment.

The project is built under the folder `rindus_ct` (aka rindus coding task). Choose that folder as the root folder for all the commands and files that are described in subsequent chapters:

`cd rindus_ct`

The project has been developed with Django and Django Rest Framework. The additional libraries and dependencies used can be found in the file `requirements.txt`


## 1.1. Running the service without Docker

The service can be run without docker with the django development server. The first time the project is run this way, the database migrations should be done with:

`python3 manage.py makemigrations`

`python3 manage.py migrate`

And after that run the development server with:

`python3 manage.py runserver`

Please note that the project uses a PostgreSQL database that needs to be configured before the django app is run. To avoid this step, we can use Docker and docker compose to use containerized PostgreSQL and Django containers that will connect with each other. This is explained in the next section.


## 1.2. Running the service with Docker and docker compose

Execute the following command to build the django app into a docker image and run the django and postgresql containers:

`sudo docker compose up` 

Once the containers are running, type this command to look for the container IDs:

`sudo docker images`

Once we know the container ID of the django application, we can access the virtualized bash console to execute the necessary commands with:

`sudo docker exec -t -i <container-id> bash`


# 2. Django command to import placeholder data

To import the data from the placeholder, execute:

`python3 manage.py import_placeholder_data`

This command will download the posts and comments from https://jsonplaceholder.typicode.com/ and it will save it to the postgres database. The data models used to store the imported data in the database can be found in `rindus_ct/res_api/models.py`

This command requires an empty database to work. If the database is not empty, it will return an error message to prevent the loss of modifications.

It is also possible to delete all database data with the command:

`python3 manage.py clear_data`

After executing it, the fresh data can be imported again.

All the django CLI commands can be found under the folder `rindus_ct/rest_api/management/commands`


# 3. REST API to manage the data

## 3.1 API documentation

### 3.1.1 DRF spectacular with Swagger

For API documentation, I have used the package drf-spectacular that uses Swagger and OpenAPI to generate interactive documentation automatically from the code. To install this package, run:

`pip install drf-spectacular`

To visualize the generated documentation, please run the development server and access it at:

`http://127.0.0.1:8000/docs/`

At that page, you can look up all available requests and methods, the expected response codes and the schemas needed for requests and responses.

### 3.1.2 DRF browsable API

The default DRF browsable API can also be used for checking API commands, but in order to do it is more convenient to disable authentication of the requests.

## 3.2 Authorization and authentication

The requests are protected by token authorization and authentication. So, in order to test the API manually, it is necessary to create users manually in the Django admin site and generate tokens to use in the requests. For doing it, follow these steps:

Create a superuser with the command:

`python3 manage.py createsuperuser`

Go to the admin site at: http://127.0.0.1:8000/admin/ and log in with the superuser created

Add a token in the Auth Token section.

Go to the Swagger doc page http://127.0.0.1:8000/docs/ and authorize the requests in the upper right corner of the screen with the generated token and the prefix "Token " appended before it.

Now the requests can be manually tested in the Swagger web interface.

Request authentication can be disabled for testing setting the global variable `common_permission_level` to `permissions.AllowAny` in `rindus_ct/rest_api/views.py`


# 4. System synchronization

The system developed acts as master. This means that the data in the local database must be preserved, compared to the data in the remote placeholder, and the system must then send the appropiate REST commands to the remote placeholder to change the diverging data.

The remote placeholder schemas do not have any time information about when the last changes were done (it does not have any "last modified" field). For this reason, it is not possible to attempt an incremental synchronization based on the latest changes.

It is necessary then to do a whole synchronization between datasets. The whole remote dataset is downloaded, compared to the data in the database, and the changes are sent back to the placehodler.

Please note that this approach is less efficient than a incremental time based one, but no other option is possible if there is no time reference available.

I could also have tried an incremental synchronization based on the HTTP header "Last-Modified" returned by the server, but that approach has been discarded in my implementation.

The synchronization is triggered running the django command:

`python3 manage.py synchronize`


# 5. Testing

## 5.1 Testing manually

The API can be tested manually through CLI curl commands, or through the Swagger browsable API as it has been described in the previous sections.


## 5.2 Automated tests

A test suite is included in `rindus_ct/rest_api/tests`. To execute the tests, run:

`python3 manage.py test`


# 6. Pending improvements

Due to lack of time, there are quite a few things that need to be improved but haven't been completed. The most important are:

- Add asynchronous support to requests to improve system performance (asyncio functionality)
- Add OpenAPI schemas to DRF views to generate automatic Swagger documentation for the responses with all response codes in the docs
- Modify settings.py file to add security recommendations from the django documentation, as if the service was to be put in production.
