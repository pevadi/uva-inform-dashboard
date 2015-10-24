from django.shortcuts import render
from django.http import HttpResponse

import requests
import tempfile
import zipfile
import shutil

def get_zip(request):
    try:
        query_string = '?'
        for k,v in request.GET.items():
            query_string += k+'='+v+'&'

        old_file = requests.get('http://cdn.mprog.nl/prog-ai/pset1.zip')
        temp_file = tempfile.TemporaryFile()
        temp_file.write(old_file.content)
        
        temp_dir = tempfile.mkdtemp()
        zipfile.ZipFile(temp_file).extractall(path=temp_dir)

        log = open(temp_dir+'/logs.sh', 'w')
        log.write('#!/bin/bash/\n')
        log.write('wget -q "http://localhost:8000/storage/store/compile/')
        log.write(query_string[:-1]+'" -O /dev/null\n')
        log.write('if [ $? = 0 ]; then rm $0; fi;\n')
        log.flush()

        make = open(temp_dir+'/Makefile', 'a')
        make.write('\nifneq ($(wildcard logs.sh),)\n')
        make.write('$(shell bash logs.sh)\nendif\n')
        make.flush()

        temp_dir2 = tempfile.mkdtemp()
        shutil.make_archive(temp_dir2+'/pset', 'zip', temp_dir)
        new_file = open(temp_dir2+'/pset.zip', 'rb')
        
        data = new_file.read() 
        response = HttpResponse(data, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="pset1.zip"'
        
        return response
    except Exception as e:
        print e
        return HttpResponse()
    finally:
        temp_file.close()
        log.close()
        new_file.close()
        shutil.rmtree(temp_dir, True)
        shutil.rmtree(temp_dir2, True)


def log_compile(request):
    print request.GET
    return HttpResponse()
