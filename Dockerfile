FROM ubuntu:latest
MAINTAINER Charles Tapley Hoyt "cthoyt@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install .
ENTRYPOINT ["python"]
CMD ["-m", "pybel_tools", "web", "--host", "0.0.0.0"]
