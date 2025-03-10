#!/usr/bin/perl
use strict;
use warnings;
use lib qw(/var/www/html/bugzilla);
use Bugzilla;
BEGIN { Bugzilla->extensions(); }
use Bugzilla::Constants;
use Bugzilla::Util;
use Bugzilla::Config qw(:admin);

Bugzilla->usage_mode(USAGE_MODE_CMDLINE);

# Настройки REST API
eval {
    SetParam('proxy_url', '');
    SetParam('webservice_error_mask', 0);
    SetParam('debug_mode', 1);
    write_params();
    print "REST API настройки обновлены\n";
};

if ($@) {
    print "Ошибка при обновлении настроек: $@\n";
    print "Продолжаем без изменения настроек...\n";
} 