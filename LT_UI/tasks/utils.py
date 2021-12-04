from pathlib import Path
from . import workers
import zipfile, os, tempfile, subprocess, re, traceback
import operator
from datetime import datetime, timedelta

def convert_to_wav(source, ext):

    with tempfile.NamedTemporaryFile(mode='w+b', suffix=ext) as sourcefile, \
        tempfile.NamedTemporaryFile(mode='r+b', suffix='.wav') as resultfile:

        sourcefile.write(source)

        command = ['ffmpeg', '-nostdin', '-y', '-i', sourcefile.name, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', resultfile.name]
        p = subprocess.run(command, text=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return (resultfile.read(), '---STDOUT---\n' + p.stdout + '\n---STDERR---\n' + p.stderr, )


def segment_audio(audio, name):
    
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.wav') as sourcefile, \
        tempfile.NamedTemporaryFile(mode='r+', suffix='.seg') as resultfile:

        sourcefile.write(audio)

        command = ['./worker_scripts/segment_audio.sh', sourcefile.name, resultfile.name, name]
        p = subprocess.run(command, text=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return (resultfile.read(), '---STDOUT---\n' + p.stdout + '\n---STDERR---\n' + p.stderr, )

def format_seg_as_stm(segmentation):

    #TODO is sorting really necessary or is seg already in order


    dic = {}
    for line in segmentation.splitlines():
        name0, name1, start_str, end_str = line.split()
        start = float(start_str)
        end = float(end_str)
        dic[start] = f'{name0}_{int(start*100):07}_{int(end*100):07} {name1} {start:.2f} {end:.2f}\n'
    
    result = [ line for _, line in sorted(dic.items()) ]

    return ''.join(result)


def stm_to_vtt_time(time):
    td = timedelta( seconds=round(float(time), 3) )
    #dummy date, important is the time 00:00:00.000000
    time = datetime(1970, 1, 1)
    #we need the datetime, since time + timedelta isn't supported
    time += td
    time = time.time()
    return time.isoformat('milliseconds')

def set_to_vtt(text, subtask):
    result = f'WEBVTT \n\nNOTE {subtask.id}\n\n'
    log = ""
    for line in text.splitlines():
        line = line.strip()     
        try:
            start, end, *hypo = line.split()
        except ValueError:
            log += f'badly formatted line {line}'
            continue
        hypo = ' '.join(hypo)
        start = stm_to_vtt_time(start)
        end = stm_to_vtt_time(end)
        result += f"{start} --> {end} \n"
        result += hypo + "\n\n"

    return result, log


def run_workers(task):

    task.status = task.PROCESSING
    task.save()

    for subtask in task.subtask.all():


        #TODO reading the whole file to pass it to workers might cause memory issues
        with subtask.source.open('rb') as src_file, subtask.result.open('wb') as res_file, subtask.log.open('wb') as log_file:
            with zipfile.ZipFile(res_file, 'w') as res_zip, zipfile.ZipFile(log_file, 'w') as log_zip:

                try:

                    source = src_file.read()
                    ext = Path(src_file.name).suffix
                    name = Path(src_file.name).stem

                    #Convert
                    audio, log = convert_to_wav(source, ext)
                    res_zip.writestr('audio.wav', audio)
                    log_zip.writestr('convert_audio.log', log)
                    print('Conversion done')

                    #Segmentation
                    segmentation, log = segment_audio(audio, name)
                    res_zip.writestr('segmentation.txt', segmentation)
                    log_zip.writestr('segment_audio.log', log)
                    print('Segmentation done')

                    #ToSTM
                    segmentation = format_seg_as_stm(segmentation)
                    res_zip.writestr('segmentation.stm', segmentation)
                    print('STM Done')

                    #ASR
                    text, log, *additional = workers.asr_worker(audio, segmentation, task.language)
                    res_zip.writestr('transcript.txt', text)
                    log_zip.writestr('transcribe_audio.log', log)
                    print('ASR done')

                    #ToVtt
                    try:
                        vtt, log = set_to_vtt(text, subtask)
                        res_zip.writestr('transcript.vtt', vtt)
                        log_zip.writestr('text_to_vtt.log', log)
                    except Exception:
                        log_zip.writestr('text_to_vtt.log', traceback.format_exc())
                    print('Vtt done')

                    #MT
                    if task.translations:
                        for code, translation, log in workers.mt_worker(text, task.language, task.translations, source, segmentation, *additional):
                            res_zip.writestr(f'translation_{code}.txt', translation)
                            log_zip.writestr(f'translate_to_{code}.log', log)
                    print('MT done')

                except Exception:
                    log_zip.writestr('error.log', traceback.format_exc())

    task.status = task.DONE
    task.save()
