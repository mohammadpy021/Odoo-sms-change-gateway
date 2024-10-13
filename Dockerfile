# Use Python base image with minimal setup
FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  libxml2-dev \
  libxslt-dev \
  libjpeg-dev \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev \
  python3-dev \
  python3-pip \
  wget \
  git \
  && rm -rf /var/lib/apt/lists/*

# Clone the Odoo 17.0 branch
# RUN git clone --depth 1 -b 17.0 https://github.com/odoo/odoo.git /usr/src/odoo

# Set the working directory
WORKDIR /usr/src/odoo

# Copy the local Odoo source code to the container
COPY . .

# change app dir
WORKDIR /usr/src/odoo/odoo

# Install Python dependencies from Odoo
RUN pip3 install -r requirements.txt

# Expose Odoo port
EXPOSE 8069

# Command to run Odoo with your custom addons path
CMD ["./odoo-bin", "--addons-path=addons/", "-d",  "odoo-db", "-r",  "odoo", "-w",  "odoo", "-i", "base", "--db_host=odoo-db", "--db-filter=^odoo-db$"]