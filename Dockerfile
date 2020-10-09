# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev mus1-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
#RUN pip install -r requirements.txt
RUN pip install aenum==2.2.2
RUN pip install aldryn-boilerplates==0.8.0
RUN pip install aldryn-forms==4.0.1
RUN pip install arrow==0.15.5
RUN pip install astroid==2.3.1

# need to check the correct version
# RUN pip install atomicwrites==1.3.0         
RUN pip install attrs==19.3.0
RUN pip install backports.csv==1.0.7
RUN pip install beautifulsoup4==4.8.1
RUN pip install binaryornot==0.4.4
RUN pip install bleach==3.1.0
RUN pip install cached-property==1.5.1

# need to check the correct version, cache iss
# RUN pip install cachetools==3.1.1
# RUN pip install certifi==2019.9.11
RUN pip install chardet==3.0.4
RUN pip install Click==7.0
RUN pip install cmsplugin-filer==1.1.3
RUN pip install colorama==0.4.1
RUN pip install cookiecutter==1.6.0
RUN pip install cookiecutter-repo-extensions==0.2.1

# need to check the version
# RUN pip install coreapi==2.3.3
RUN pip install coreschema==0.0.4
RUN pip install coverage==4.0.3
RUN pip install cssselect==1.1.0
RUN pip install cssutils==1.0.2
RUN pip install defusedxml==0.6.0
RUN pip install diff-match-patch==20181111
RUN pip install Django==1.11.25
RUN pip install django-absolute==0.3
RUN pip install django-allauth==0.33.0
RUN pip install django-appconf==1.0.3
RUN pip install django-argonauts==1.2.0
RUN pip install django-classy-tags==0.9.0
RUN pip install django-cms==3.6.0
RUN pip install django-compressor==2.3

# RUN pip install django-contrib-comments==1.9.1
# RUN pip install django-cors-headers==3.1.1
RUN pip install django-crispy-forms==1.6.0

RUN pip install django-debug-toolbar==1.4
RUN pip install django-emailit==0.2.4
RUN pip install django-enumfield==1.5
RUN pip install django-enumfields==1.0.0
RUN pip install django-extensions==2.2.3
RUN pip install django-filer==1.5.0
RUN pip install django-filter==2.2.0
RUN pip install django-formtools==2.1
RUN pip install django-import-export==1.2.0
RUN pip install django-inlinecss==0.3.0
RUN pip install django-ipware==2.1.0
RUN pip install django-jet==1.0.8
RUN pip install django-js-asset==1.2.2
RUN pip install django-mptt==0.10.0
RUN pip install django-polymorphic==2.0.3
RUN pip install django-pyscss==2.0.2
RUN pip install django-ranged-response==0.2.0
RUN pip install django-rest-auth==0.9.5
RUN pip install django-rest-passwordreset==1.1.0
RUN pip install django-rest-swagger==2.2.0
RUN pip install django-reversion==1.10.2
RUN pip install django-sekizai==1.0.0
RUN pip install django-settings-export==1.1.0
RUN pip install django-simple-captcha==0.5.12
RUN pip install django-sizefield==1.0.0
RUN pip install django-tablib==3.2
RUN pip install django-treebeard==4.3
RUN pip install django-webpack-loader==0.3.0
RUN pip install django-widgy==0.9.0
RUN pip install djangocms-admin-style==1.4.0
RUN pip install djangocms-attributes-field==1.1.0
RUN pip install djangocms-column==1.9.0
RUN pip install djangocms-file==2.3.0
RUN pip install djangocms-forms==0.2.5
RUN pip install djangocms-googlemap==1.3.0
RUN pip install djangocms-inherit==0.2.2
RUN pip install djangocms-link==2.5.0
RUN pip install djangocms-picture==2.1.3
RUN pip install djangocms-rest-api==0.2.0
RUN pip install djangocms-snippet==2.1.0
RUN pip install djangocms-style==2.2.0
RUN pip install djangocms-text-ckeditor==3.7.0
RUN pip install djangocms-video==2.1.1
RUN pip install djangorestframework==3.10.3
RUN pip install djangorestframework-jwt==1.11.0
RUN pip install dodgy==0.2.1
RUN pip install drf-renderer-xlsx==0.3.5
RUN pip install easy-thumbnails==2.6
RUN pip install entrypoints==0.3
RUN pip install et-xmlfile==1.0.1
RUN pip install filebrowser-safe==0.5.0
RUN pip install flake8==3.5.0
RUN pip install flake8-polyfill==1.0.2
RUN pip install fqdn==1.1.0

# non-checked list
# RUN pip install future==0.18.0
# RUN pip install grappelli-safe==0.5.2
# RUN pip install gremlinpython==3.4.4
# RUN pip install hashids==1.2.0
# RUN pip install html2text==2019.9.26
# RUN pip install html5lib==1.0.1
# RUN pip install httpie==1.0.3
# RUN pip install idna==2.8
# RUN pip install importlib-metadata==1.4.0
# RUN pip install isodate==0.6.0
# RUN pip install isort==4.3.21
# RUN pip install itypes==1.1.0
# RUN pip install jdcal==1.4.1
# RUN pip install jet-django==0.7.6
# RUN pip install Jinja2==2.10.3
# RUN pip install jinja2-time==0.2.0
# RUN pip install jsonfield==2.0.2
# RUN pip install lazy-object-proxy==1.4.2
# RUN pip install lxml==4.4.1
# RUN pip install Markdown==3.1.1
# RUN pip install MarkupSafe==1.1.1
# RUN pip install mccabe==0.6.1
# RUN pip install Mezzanine==4.3.1
# RUN pip install more-itertools==8.1.0
# RUN pip install neobolt==1.7.15
# RUN pip install neotime==1.7.4
# RUN pip install oauthlib==3.1.0
# RUN pip install odfpy==1.4.0
# RUN pip install openapi-codec==1.3.2
# RUN pip install openpyxl==2.4.9
# RUN pip install pep257==0.7.0
# RUN pip install pep8==1.7.1
# RUN pip install pep8-naming==0.9.1
# RUN pip install phonenumbers==8.10.20
# RUN pip install Pillow==6.2.0
# RUN pip install pipenv==2018.11.26
# RUN pip install pluggy==0.13.1
# RUN pip install poyo==0.5.0
# RUN pip install premailer==3.6.1
# RUN pip install prompt-toolkit==2.0.10
# RUN pip install prospector==0.11.7
# RUN pip install psycopg2==2.7.7
# RUN pip install psycopg2-binary==2.8.4
# RUN pip install py==1.8.1
# RUN pip install pycodestyle==2.3.1
# RUN pip install pyflakes==1.6.0
# RUN pip install Pygments==2.4.2
# RUN pip install PyJWT==1.7.1
# RUN pip install pylint==2.4.2
# RUN pip install pylint-celery==0.3
# RUN pip install pylint-common==0.2.5
# RUN pip install pylint-django==2.0.13
# RUN pip install pylint-flask==0.6
# RUN pip install pylint-plugin-utils==0.6
# RUN pip install pynliner==0.8.0
# RUN pip install pyScss==1.3.5
# RUN pip install pytest==3.9.1
# RUN pip install pytest-cookies==0.3.0
# RUN pip install pytest-django==2.9.1
# RUN pip install python-dateutil==2.8.1
# RUN pip install python3-openid==3.1.0
# RUN pip install pytz==2019.3
# RUN pip install PyYAML==5.1.2
# RUN pip install rcssmin==1.0.6
# RUN pip install requests==2.22.0
# RUN pip install requests-oauthlib==1.2.0
# RUN pip install requirements-detector==0.6
# RUN pip install rjsmin==1.1.0
# RUN pip install setoptconf==0.2.0
# RUN pip install simplejson==3.17.0
# RUN pip install six==1.12.0
# RUN pip install sorl-thumbnail==12.5.0
# RUN pip install soupsieve==1.9.4
# RUN pip install sqlparse==0.3.0
# RUN pip install stringcase==1.2.0
# RUN pip install tablib==0.13.0
# RUN pip install tg-utils==0.4.0
# RUN pip install tornado==4.5.3
# RUN pip install typed-ast==1.4.0
# RUN pip install tzlocal==2.0.0
# RUN pip install Unidecode==1.0.23
# RUN pip install uritemplate==3.0.1
# RUN pip install urllib3==1.25.7
# RUN pip install virtualenv==16.7.9
# RUN pip install virtualenv-clone==0.5.3
# RUN pip install wcwidth==0.1.7
# RUN pip install webencodings==0.5.1
# RUN pip install whichcraft==0.6.1
# RUN pip install wrapt==1.11.2
# RUN pip install xlrd==1.2.0
# RUN pip install xlwt==1.3.0
# RUN pip install YURL==1.0.0
# RUN pip install zipp==1.0.0

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
