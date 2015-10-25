from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest,\
        HttpResponseRedirect
from django.template import loader, RequestContext

import requests
import tempfile
import zipfile
import shutil

from identity import identity_required

@identity_required
def get_zip(request):
    filepath = request.GET.get("f", None)
    if filepath is None:
        return HttpResponseBadRequest()

    filename = filepath.split("/")[-1]

    old_file = requests.get(filepath)
    if not old_file.status_code == 200:
        return HttpResponseRedirect(filepath)

    try:
        temp_file = tempfile.TemporaryFile()
        temp_file.write(old_file.content)

        temp_dir = tempfile.mkdtemp()
        zipfile.ZipFile(temp_file).extractall(path=temp_dir)

        log = open(temp_dir+'/logs.sh', 'w')
        loader_template = loader.get_template("compile_log.sh")
        log.write(loader_template.render(
            RequestContext(request, {'pset': filepath})))
        log.flush()


        make = open(temp_dir+'/Makefile', 'r')
        target_found = False
        makefile_content = []
        for line in make.readlines():
            if line[:4] == "all:":
                target_found = True
            if target_found and line == "\n":
                makefile_content.append('\nifneq ($(wildcard logs.sh),)\n')
                makefile_content.append('\t$(shell /bin/bash logs.sh)\nendif\n')
                target_found = False
            makefile_content.append(line)

        make = open(temp_dir+'/Makefile', 'w')
        make.write("".join(makefile_content))
        make.flush()

        temp_dir2 = tempfile.mkdtemp()
        shutil.make_archive(temp_dir2+'/pset', 'zip', temp_dir)
        new_file = open(temp_dir2+'/pset.zip', 'rb')

        data = new_file.read()
        response = HttpResponse(data, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename,)
        return response
    except Exception as e:
        return HttpResponse(str(e), status=500)
    finally:
        if 'temp' in locals():
            temp_file.close()
        if 'log' in locals():
            log.close()
        if 'make' in locals():
            make.close()
        if 'new_file' in locals():
            new_file.close()
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, True)
        if 'temp_dir2' in locals():
            shutil.rmtree(temp_dir2, True)


