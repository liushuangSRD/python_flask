# 指定所创建镜像的基础镜像
FROM ubuntu
LABEL author="xxx"
#用ubuntu国内源替换默认源
RUN rm /etc/apt/sources.list
COPY sources.list /etc/apt/sources.list

WORKDIR /app
ADD . /app

#安装python
RUN apt-get update
RUN apt-get install -y python python-pip
RUN pip install --upgrade pip

# 安装依赖
RUN pip install -r requirements.txt
# 声明镜像内服务监听的端口
EXPOSE 80

CMD ["python", "app.py"]