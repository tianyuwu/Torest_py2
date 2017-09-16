FROM python:2.7

EXPOSE 8080

ENV PYTHONUNBUFFERED 0
#RUN apt-get update && apt-get install -y mysql-client

# based on python:2.7-onbuild, but if we use that image directly
# the above apt-get line runs too late.
# RUN mkdir -p /usr/src/app
# WORKDIR /usr/src/app
ADD . /code
WORKDIR /code

# 使用阿里云的pip镜像,copy的文件属于当前dockerfile的相对目录
COPY pip.conf /root/.pip/pip.conf

# 这是workdir所指的目录
RUN pip install -r requirements.txt


# CMD python app.py --mysql_host=mysql
CMD ["python", "-u", "app.py"]