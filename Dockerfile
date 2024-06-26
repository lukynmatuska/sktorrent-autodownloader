FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN echo "Used user id: ${USER_ID}\nUsed group id: ${GROUP_ID}"

# Update system and install packages
RUN apt update &&\
    apt upgrade -y &&\
    apt autoremove -y &&\
    apt install -y git

# Upgrade python package manager
RUN pip install pdm

# Change working directory
WORKDIR /var/www

# Copy folders and files – It's important to copy files before changing their ownership
COPY ./.git ./.git
COPY ./pyproject.toml ./pyproject.toml
COPY ./src ./src

# Change ID of www-data user and group to ID from ENV
RUN if [ ${USER_ID:-0} -ne 0 ] && [ ${GROUP_ID:-0} -ne 0 ]; then \
    if getent passwd www-data ; then echo "Delete user www-data" && userdel -f www-data;fi &&\
    if getent group www-data ; then echo "Delete group www-data" && groupdel www-data;fi &&\
    echo "Add new group www-data" && groupadd -g ${GROUP_ID} www-data &&\
    echo "Add new user www-data" && useradd -l -u ${USER_ID} -g www-data www-data &&\
    echo "Change ownership of workdir" && mkdir -p /var/www && chown --changes --no-dereference --recursive www-data:www-data /var/www &&\
    echo "Change ownership of homedir" && mkdir -p /home/www-data && chown --changes --no-dereference --recursive www-data:www-data /home/www-data \
;fi

# Change user
USER www-data:www-data

# Install dependencies
RUN pdm install

# Expose port
EXPOSE 80

# Check container status when running
HEALTHCHECK --interval=10s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health-check || exit 1

# Command on start of container
# If running behind a proxy like Nginx or Traefik add --proxy-headers
CMD bash -c "eval \$(python3 -m pdm venv activate in-project) && uvicorn --proxy-headers --forwarded-allow-ips \"*\" --host 0.0.0.0 --port 80 src.main:app"
