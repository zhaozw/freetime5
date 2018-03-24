#!/bin/sh
#redis cleann
#    eval "return redis.call('del',unpack(redis.call('keys',ARGV[1])))" 0 "sns*"
redis-cli -p 8004 << EOF
    select 1

    eval "return redis.call('del',unpack(redis.call('keys',ARGV[1])))" 0 "chat*"
    echo "clean mix"
    select 7
    eval "return redis.call('del',unpack(redis.call('keys',ARGV[1])))" 0 "chat*"
    echo "clean user 1"
    select 8
    eval "return redis.call('del',unpack(redis.call('keys',ARGV[1])))" 0 "chat*"
    echo "clean user 2"
EOF