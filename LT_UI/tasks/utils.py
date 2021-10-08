from . import workers
import zipfile

def run_workers(task):

    print('thread started')

    task.status = task.PROCESSING
    task.save()

    #TODO do seperation
    seperation = ''

    #TODO reading the whole file to pass it to workers might cause memory issues
    with task.source.open('rb') as src_file:
        with task.result.open('wb') as res_file:
            with zipfile.ZipFile(res_file, 'w') as res_zip:
                print('open files')
                source = src_file.read()
                print('launch asr')
                text = workers.asr_worker(source, seperation, task.language)
                res_zip.writestr('transcript.txt', text)
                if task.translations:
                    print('launch mt')
                    for code, translation in workers.mt_worker(text, task.language, task.translations, source, seperation):
                        res_zip.writestr(f'translation_{code}.txt', translation)

    task.status = task.DONE
    task.save()
