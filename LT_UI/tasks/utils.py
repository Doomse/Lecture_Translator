from . import workers
import zipfile, os, tempfile, subprocess, re, traceback
import operator
from datetime import timedelta

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

def stm_to_vtt_time(time):
    time_orig = float(time)
    time = str(timedelta(seconds=time_orig))
    time = "0" +time
    split_ms = time.split('.')
    if len(split_ms) < 2:
        time = time + ".000"
    else:
        time = round(float("0."+split_ms[1]), 3)
        time = split_ms[0] + str(time)[1:]
        split_ms = time.split('.')
        ms_len =  len(split_ms[1])
        if ms_len <= 3:
            time = time + "0"*(3-ms_len)
    return time

def set_to_vtt(text):
    result = "WEBVTT \n\n"
    for line in text.split('\n'):
        line = line.strip()     
        if len(line) < 2:
            print("line to short: {}".format(line))
            continue   
        print(line)
        tokens = line.split()       
        start, end = tokens[0], tokens[1]
        hypo = ' '.join(tokens[2:])
        start = stm_to_vtt_time(start)
        end = stm_to_vtt_time(end)
        result += "{} --> {} \n".format(start, end)
        result += hypo + "\n\n"

    return result, "None"


def seg_to_stm(seg):
    dic = {}
    dic2 = {}
    for line in seg.splitlines():
        tokens = line.split()
        if "." not in tokens[2]:
            tokens[2] = tokens[2] + ".00"
        if "." not in tokens[3]:
            tokens[3] = tokens[3] + ".00"
        start_sec, start_ms = tokens[2].split('.')
        start_ms = start_ms + '0' * (2-len(start_ms.strip()))
        start = start_sec + start_ms
        if len(start) < 7:
            rest = 7-len(start)
            rest_s = "0"*rest
            start = rest_s + start
        end_sec, end_ms = tokens[3].split('.')
        end_ms = end_ms + '0' * (2-len(end_ms.strip()))
        end = end_sec + end_ms
        if len(end) < 7:
            rest = 7-len(end)
            rest_s = "0"*rest
            end = rest_s + end
        utt_id = tokens[0]+"_"+start+"_"+end
        dic[utt_id] = float(tokens[2])
        dic2[utt_id] = (tokens[1], tokens[2], tokens[3])

    sorted_dicdata = sorted(dic.items(), key=operator.itemgetter(1))
    result=""
    for tpl in sorted_dicdata:
        lst = dic2[tpl[0]]
        start_sec, start_ms = lst[1].split('.')
        start = start_sec + "." + start_ms + '0' * (2-len(start_ms))
        end_sec, end_ms = lst[2].split('.')
        end = end_sec + "." + end_ms + '0' * (2-len(end_ms))
        str_ = "{} {} {}".format(lst[0], start, end)            
        out = tpl[0] + " "+ str_
        result += out + "\n"  

    return result

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
                    segmentation = seg_to_stm(segmentation)
                    res_zip.writestr(f'segmentation/{folder}.stm', segmentation)
                    print('STM DONE')

                    #ASR
                    text, log, *additional = workers.asr_worker(audio, segmentation, task.language)
                    res_zip.writestr(f'{folder}/transcript.txt', text)
                    res_zip.writestr(f'transcript/{folder}.txt', text)
                    log_zip.writestr(f'{folder}/transcribe_audio.log', log)
                    print('ASR done')

                    1#ToVtt
                    try:
                        #vtt, log = text_to_vtt(text, task.language)
                        vtt, log = set_to_vtt(text)
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
