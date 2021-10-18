from . import workers
import zipfile

def run_workers(task):

    task.status = task.PROCESSING
    task.save()

    #TODO reading the whole file to pass it to workers might cause memory issues
    with task.source.open('rb') as src_file:
        with task.result.open('wb') as res_file:
            with zipfile.ZipFile(res_file, 'w') as res_zip:
                source = src_file.read()
                seperation = workers.sep_worker(source, task.language)
                res_zip.writestr('seperation.txt', seperation)
                text = workers.asr_worker(source, seperation, task.language)
                res_zip.writestr('transcript.txt', text)
                if task.translations:
                    for code, translation in workers.mt_worker(text, task.language, task.translations, source, seperation):
                        res_zip.writestr(f'translation_{code}.txt', translation)

    task.status = task.DONE
    task.save()
