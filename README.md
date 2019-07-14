# monkeys

A web application written in Python using Flask, Postgres and SQLAlchemy. Default deployment platform is Heroku, although with some tweaking it can run on any server using gunicorn. Demo version can be found [here](https://qqalexqq-monkeys.herokuapp.com/).

## Deployment

To deploy your own version of application on Heroku proceed with this steps:

1. Install Fabric:
`pip install fabric`
2. Clone this repo:
`git clone https://github.com/qqalexqq/monkeys`
3. Prepare heroku application:
`fab prepare_heroku`
4. Deploy on the newly created application:
`fab deploy`
5. Scale dynos to actually run the application:
`heroku ps:scale web=1`

Both `prepare_heroku` and `deploy` commands can take an argument, which will be used to give the name of `git remote` you wish to use.

## Development

1. Clone this repo and into it:
`git clone https://github.com/qqalexqq/monkeys && cd monkeys`
2. Create virtual environment:
`mkvirtualenv 'env_name' or `virtualenv 'env_name'`
3. Source virtual environment:
`. ''env_name''/bin/activate`
4. Install dependencies into virtual environment:
`pip install -r requirements.txt`
5. Create development and testing databases in Postgres (psql):

`CREATE DATABASE ''database_name''`

`CREATE DATABASE ''test_database_name''`

6. Set environmental variables for database and application running:

`export APP_SETTINGS="config.DevelopmentConfig"`

`export DATABASE_URL="postgresql://localhost/''database_name''"`

`export TEST_DATABASE_URL="postgresql://localhost/''test_database_name''"`

7. Upgrade database using migrations:
`python manage.py db upgrade`
8. Run tests to see if nothing is broken:
`python manage.py test`
9. Run the actual application:
`python manage.py runserver`

Note: if you change something and want to deploy it, there is a `fab prepare_deployment` command, which takes care of testing, requirements, commiting and pushing changes in git.

## License

[MIT](./LICENSE).
