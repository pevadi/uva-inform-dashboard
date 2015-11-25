#/bin/bash/
# This file logs the first time you compiled your assignment. This is used in
# the Learning Analytics project run by the University of Amsterdam.
wget -q "{{ request.scheme }}://{{ request.get_host }}{% url 'storage:store_compile_event' %}?{{ request.signed_url_params|safe }}" --post-data="pset={{ pset|escape }}" -O /dev/null
if [ $? = 0 ]; then rm "$0"; fi;
