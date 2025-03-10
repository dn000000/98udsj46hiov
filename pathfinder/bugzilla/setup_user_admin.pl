#!/usr/bin/perl
use strict;
use warnings;
use lib qw(/var/www/html/bugzilla);
use Bugzilla;
BEGIN { Bugzilla->extensions(); }
use Bugzilla::Constants;
use Bugzilla::User;
use Bugzilla::Group;

Bugzilla->usage_mode(USAGE_MODE_CMDLINE);

# Получаем пользователя developer
my $dbh = Bugzilla->dbh;
my $login = 'developer@example.com';
my $user_id = $dbh->selectrow_array(
    "SELECT userid FROM profiles WHERE login_name = ?",
    undef, $login
);

unless ($user_id) {
    die "Пользователь $login не найден!\n";
}

# Добавляем пользователя во все группы, включая admin
print "Предоставление всех прав пользователю $login...\n";

# Получаем все группы
my $group_ids = $dbh->selectall_arrayref(
    "SELECT id FROM groups"
);

foreach my $group_id (@$group_ids) {
    $dbh->do(
        "INSERT IGNORE INTO user_group_map (user_id, group_id, isbless, grant_type) 
         VALUES (?, ?, 0, 0)",
        undef, $user_id, $group_id->[0]
    );
}

print "Права успешно предоставлены!\n"; 