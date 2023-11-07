FROM public.ecr.aws/lambda/python:3.8

# Copy data and install base package
COPY . ${LAMBDA_TASK_ROOT}
RUN yum -y install wget tar make

#Permission on chainfiles
RUN chmod -R 755 ${LAMBDA_TASK_ROOT}/chainfiles

# Install Python requirements packages
RUN yum -y install python3 python3-pip
RUN pip3 install -r requirements.txt

# Install R and dependencies
ENV R_VERSION=4.2.0
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
  && wget https://cdn.rstudio.com/r/centos-7/pkgs/R-${R_VERSION}-1-1.x86_64.rpm \
  && yum -y install R-${R_VERSION}-1-1.x86_64.rpm \
  && rm R-${R_VERSION}-1-1.x86_64.rpm
ENV PATH="${PATH}:/opt/R/${R_VERSION}/bin/"

# System requirements for R packages
RUN yum -y install openssl-devel
RUN Rscript -e "install.packages(c('data.table','xgboost'),repos = 'https://packagemanager.rstudio.com/all/__linux__/centos7/latest' )"

# Install XCNV
#RUN tar -xf XCNV.tar.gz
#RUN chmod -R 755 ${LAMBDA_TASK_ROOT}/XCNV
#WORKDIR ${LAMBDA_TASK_ROOT}/XCNV
#RUN ./Install.sh
#WORKDIR ${LAMBDA_TASK_ROOT}

# Lambda entry point
CMD ["xcnv_lambda.handler"]
