'''Fabfile for application deployment.'''
from fabric.api import local, prompt


def prepare_heroku(remote_name='production'):
    app_name = prompt('New heroku application name: ')
    config_type = 'Production' if remote_name == 'production' else 'Staging'

    local(
        'heroku apps:create --region eu {0} --remote {1}'
        .format(app_name, remote_name)
    )
    local(
        'heroku config:set APP_SETTINGS=config.{0}Config --remote {1}'
        .format(config_type, remote_name)
    )
    local('heroku addons:add --app {0} heroku-postgresql'.format(app_name))
    local('heroku pg:promote --app {0} DATABASE_URL'.format(app_name))


def prepare_deployment():
    commit_comment = prompt('Enter your git commit comment: ')

    # TODO: add testing
    local('pip freeze > requirements.txt')
    local('git add -A')
    local('git commit -m "{0}"'.format(commit_comment))
    local('git push -u origin master')


def deploy(remote_name='production'):
    local('heroku maintenance:on')
    local('git push {0} master'.format(remote_name))
    local('heroku maintenance:off')
