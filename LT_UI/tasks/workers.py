import time

"""
Specify the list of languages your ASR system supports by filling this list with tuples of code (max 5 chars) and display name.

Example:
LANGUAGE_CHOICES = [
    ('de', 'German'),
    ('en', 'English'),
]
"""
LANGUAGE_CHOICES = [
    
]


"""
Specify the list of languages your MT system supports for a given source language.
You can do this by filling this dictionary with a source language key and a list of translations as values.
The translation lists of consist (similarly to the LANGUAGE_CHOICES) of tuples of code (max 5 chars) and display name.

Example:
TRANSLATION_CHOICES = {
    'de': [
        ('en', 'English'),
    ],
    'en': [
        ('de', 'German'),
        ('fr', 'French'),
    ],
}
"""
TRANSLATION_CHOICES = {
    
}


"""
Implement your seperation worker interface in this function.
Please note that this functions is potentially called in parallel,
so if your workers rely on unique resources, you have to take care of synchronisation.

'source' is the content of the uploaded file.
'language' is one of the language codes specified in LANGUAGE_CHOICES.

Expects the result of the seperation process.
"""
def sep_worker(source: bytes, language: str) -> str:
    return 'seperation'


"""
Implement your ASR worker interface in this function.
Please note that this functions is potentially called in parallel,
so if your workers rely on unique resources, you have to take care of synchronisation.

'source' is the content of the uploaded file.
'seperation' is the content of the seperation file.
'language' is one of the language codes specified in LANGUAGE_CHOICES.

Expects the result of the ASR process.
"""
def asr_worker(source: bytes, seperation: str, language: str) -> str:
    return 'transcription'


"""
Implement your MT worker interface in this function.
Please note that this functions is potentially called in parallel,
so if your workers rely on unique resources, you have to take care of synchronisation.

'text' is the result of the ASR worker.
'language' is one of the language codes specified in LANGUAGE_CHOICES.
'translations' is a list of language codes specified in TRANSLATION_CHOICES.
'source' is the content of the uploaded file.
'seperation' is the content of the seperation file.

Expects the results of all MT processes returned as (language_code, translation) tuples.
They can either be returned as a list or using 'yield' (a generator).
"""
def mt_worker(text: str, language: str, translations: 'list[str]', source: bytes, seperation: str) -> 'list[tuple[str,str]]':
    return [f'{code} translation' for code in translations]