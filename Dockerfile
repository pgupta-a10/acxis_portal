############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:14.04

ENV DJANGO_PRODUCTION=false

MAINTAINER Priyesh Gupta

# Install packages
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    mysql-client \
    python-dev \
    python-mysqldb \
    python-setuptools \
    #python-urllib3 \
    python-ldap \
    #supervisor \
    vim
#RUN apt-get install python-bs4
RUN easy_install pip
RUN easy_install setuptools==18.5


# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
#ENV DOCKYARD_SRC=acxis_portal
ENV DOCKYARD_SRC=.

# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv

# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/srv/acxis_portal

RUN mkdir $DOCKYARD_SRVPROJ

# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME

RUN mkdir media static logs

VOLUME ["$DOCKYARD_SRVHOME/logs/"]

# Copy application source code to SRCDIR
#COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

#copy requirements.txt file. Since we are mapping source code for development, we need to do this.
#Else this is not needed.
COPY $DOCKYARD_SRC/requirements.txt $DOCKYARD_SRVPROJ

# Install Python dependencies
RUN pip install -r $DOCKYARD_SRVPROJ/requirements.txt

# configure nginx
#RUN ln -s $DOCKYARD_SRVPROJ/nginx.conf /etc/nginx/sites-enabled/django_docker.conf
#RUN rm /etc/nginx/sites-enabled/default

# Port to expose
EXPOSE 9000

# Copy entrypoint script into the image
WORKDIR $DOCKYARD_SRVPROJ

COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
