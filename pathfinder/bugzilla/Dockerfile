FROM centos:7

# Настройка репозиториев на архивные зеркала
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Установка репозитория EPEL и базовых пакетов
RUN yum -y update && \
    yum -y install epel-release && \
    yum -y install perl perl-CPAN perl-DBD-MySQL make gcc-c++ && \
    yum -y install perl-core perl-App-cpanminus && \
    yum -y install gcc gd gd-devel rst2pdf graphviz patchutils && \
    yum -y install httpd httpd-devel && \
    yum -y install wget nano mysql procps-ng less file && \
    yum clean all

# Установка Perl модулей через yum
RUN yum -y install \
    perl-CGI \
    perl-DateTime \
    perl-DateTime-TimeZone \
    perl-Template-Toolkit \
    perl-Email-MIME \
    perl-URI \
    perl-List-MoreUtils \
    perl-JSON-XS \
    perl-GD \
    perl-MIME-tools \
    perl-XML-Twig \
    perl-HTML-Parser \
    perl-HTML-Scrubber \
    perl-Encode-Detect \
    perl-TimeDate \
    perl-IO-stringy \
    perl-libwww-perl && \
    yum clean all

# Установка оставшихся Perl модулей через cpanm
RUN cpanm -f Email::Sender Math::Random::ISAAC Email::Reply PatchReader

# Скачивание и установка Bugzilla из GitHub
RUN wget https://github.com/bugzilla/bugzilla/archive/refs/tags/release-5.0.4.tar.gz && \
    mkdir -p /opt && \
    tar -C /opt -zxvf release-5.0.4.tar.gz && \
    mv /opt/bugzilla-release-5.0.4 /opt/bugzilla-5.0.4 && \
    ln -s /opt/bugzilla-5.0.4 /var/www/html/bugzilla && \
    rm release-5.0.4.tar.gz

# Создание директории данных с правильными правами доступа
RUN mkdir -p /var/www/html/bugzilla/data && \
    chown -R apache:apache /var/www/html/bugzilla && \
    chmod 755 /var/www/html/bugzilla/data

# Настройка Apache
RUN sed -i 's/^/#&/g' /etc/httpd/conf.d/welcome.conf
COPY bugzilla.conf /etc/httpd/conf.d/

# Настройка ServerName для Apache
RUN echo "ServerName localhost" >> /etc/httpd/conf/httpd.conf

# Скрипт для установки Perl модулей и настройки Bugzilla
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"] 