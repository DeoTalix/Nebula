FROM python:2.7

# Ensures that Python doesn't write compiled bytecode files to disk/
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures that Python output is unbuffered and immediately printed to the 
# console.
ENV PYTHONUNBUFFERED 1

ENV DOCKER 1

# This line sets the working directory for the image, which is where subsequent 
# commands will be run.
WORKDIR /Nebula

# This lines use pip to install the packages listed in the requirements.txt file.
RUN pip install -U --no-cache-dir pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# This line copies the entire contents of the project directory to the working 
# directory in the image. This copies all the application code, scripts, and 
# other necessary files into the image.
# COPY ./mailservice .
