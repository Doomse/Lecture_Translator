from . import workers
import zipfile, os

def run_workers(task):

    task.status = task.PROCESSING
    task.save()

    #TODO reading the whole file to pass it to workers might cause memory issues
    with task.source.open('rb') as src_file, task.result.open('wb') as res_file:
        with zipfile.ZipFile(src_file, 'r') as src_zip, zipfile.ZipFile(res_file, 'w') as res_zip:
            for filename in src_zip.namelist():
                source = src_zip.read(filename)
                folder = os.path.splitext(filename)[0]
                seperation = workers.sep_worker(source, task.language)
                res_zip.writestr(f'{folder}/seperation.txt', seperation)
                res_zip.writestr(f'seperation/{folder}.txt', seperation)
                text = workers.asr_worker(source, seperation, task.language)
                res_zip.writestr(f'{folder}/transcript.txt', text)
                res_zip.writestr(f'transcript/{folder}.txt', text)
                if task.translations:
                    for code, translation in workers.mt_worker(text, task.language, task.translations, source, seperation):
                        res_zip.writestr(f'{folder}/translation_{code}.txt', translation)
                        res_zip.writestr(f'translation_{code}/{folder}.txt', translation)

    task.status = task.DONE
    task.save()
