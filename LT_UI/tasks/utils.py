from . import workers
import zipfile, os, tempfile, subprocess, re, traceback


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


def text_to_vtt(text, lang):

    phrase = []
    vtt = f'WEBVTT Kind: captions; Language: {lang}\n\n'

    for line in text.split('\n'):

        #TODO maybe skip empty lines

        start, dur, word = line.split(' ')

        if not phrase:
            secondsFrom = float(start)
        phrase += [word]
        if re.match(r'[,\.\?\!]', word[-1]):
            secondsTo = float(start) + float(dur)

            hoursFrom=int(secondsFrom//60//60)
            minutesFrom=int((secondsFrom - 60*60*hoursFrom)//60)
            secondsFrom=secondsFrom - hoursFrom*60*60 - minutesFrom*60.0

            hoursTo=int(secondsTo//60//60)
            minutesTo=int((secondsTo - 60*60*hoursTo)//60)
            secondsTo=secondsTo - hoursFrom*60*60 - minutesTo*60.0

            vtt += f'{hoursFrom:02d}:{minutesFrom:02d}:{secondsFrom:06.3f} --> {hoursTo:02d}:{minutesTo:02d}:{secondsTo:06.3f}\n'
            vtt += ' '.join(phrase) + '\n\n'
            phrase = []

    #Roll out once to handle last phrase regardless of ending
    secondsTo = float(start) + float(dur)

    hoursFrom=int(secondsFrom//60//60)
    minutesFrom=int((secondsFrom - 60*60*hoursFrom)//60)
    secondsFrom=secondsFrom - hoursFrom*60*60 - minutesFrom*60.0

    hoursTo=int(secondsTo//60//60)
    minutesTo=int((secondsTo - 60*60*hoursTo)//60)
    secondsTo=secondsTo - hoursFrom*60*60 - minutesTo*60.0

    vtt += f'{hoursFrom:02d}:{minutesFrom:02d}:{secondsFrom:06.3f} --> {hoursTo:02d}:{minutesTo:02d}:{secondsTo:06.3f}\n'
    vtt += ' '.join(phrase) + '\n\n'

    #Edit file using sed
    command = ['sed', '-e', '"s/<unk>//g"', '-e', '"s/\s\+/ /g"', '-e', '"s/^\s*//g"']
    p = subprocess.run(command, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(vtt)

    return (p.stdout, p.stderr, )




def run_workers(task):

    task.status = task.PROCESSING
    task.save()

    #TODO reading the whole file to pass it to workers might cause memory issues
    with task.source.open('rb') as src_file, task.result.open('wb') as res_file, task.log.open('wb') as log_file:
        with zipfile.ZipFile(src_file, 'r') as src_zip, zipfile.ZipFile(res_file, 'w') as res_zip, zipfile.ZipFile(log_file, 'w') as log_zip:
            for filename in src_zip.namelist():

                try:

                    source = src_zip.read(filename)
                    folder, ext = os.path.splitext(filename)

                    #Convert
                    audio, log = convert_to_wav(source, ext)
                    res_zip.writestr(f'{folder}/audio.wav', audio)
                    res_zip.writestr(f'audio/{folder}.wav', audio)
                    log_zip.writestr(f'{folder}/convert_audio.log', log)
                    print('Conversion done')

                    #Segmentation
                    segmentation, log = segment_audio(audio, folder)
                    res_zip.writestr(f'{folder}/segmentation.txt', segmentation)
                    res_zip.writestr(f'segmentation/{folder}.txt', segmentation)
                    log_zip.writestr(f'{folder}/segment_audio.log', log)
                    print('Segmentation done')

                    #ASR
                    text, log, *additional = workers.asr_worker(audio, segmentation, task.language)
                    res_zip.writestr(f'{folder}/transcript.txt', text)
                    res_zip.writestr(f'transcript/{folder}.txt', text)
                    log_zip.writestr(f'{folder}/transcribe_audio.log', log)
                    print('ASR done')

                    #ToVtt
                    try:
                        vtt, log = text_to_vtt(text, task.language)
                        res_zip.writestr(f'{folder}/transcript.vtt', vtt)
                        res_zip.writestr(f'transcript/{folder}.vtt', vtt)
                        log_zip.writestr(f'{folder}/text_to_vtt.log', log)
                    except Exception:
                        log_zip.writestr(f'{folder}/text_to_vtt.log', traceback.format_exc())
                    print('Vtt done')

                    #MT
                    if task.translations:
                        for code, translation, log in workers.mt_worker(text, task.language, task.translations, source, segmentation, *additional):
                            res_zip.writestr(f'{folder}/translation_{code}.txt', translation)
                            res_zip.writestr(f'translation_{code}/{folder}.txt', translation)
                            log_zip.writestr(f'{folder}/translate_to_{code}.log', log)
                    print('MT done')

                except Exception:
                    log_zip.writestr(f'{folder}/error.log', traceback.format_exc())

    task.status = task.DONE
    task.save()
