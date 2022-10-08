FROM centos:latest
RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
WORKDIR /Ogame
RUN \ 
#  yum -y update && \
  rpm -Uvh https://packages.microsoft.com/config/centos/7/packages-microsoft-prod.rpm &&  \
  yum -y install aspnetcore-runtime-5.0 dotnet-sdk-5.0 wget unzip &&  \
  wget https://github.com/ogame-tbot/TBot/releases/download/v0.2.63/TBot-v0.2.63-linux64.zip && \
  unzip TBot-v0.2.63-linux64.zip
EXPOSE 8085
RUN chmod +x /Ogame/publish/linux64/TBot && chmod +x /Ogame/publish/linux64/ogamed
COPY settings.json /Ogame/publish/linux64/settings.json
CMD /bin/bash



