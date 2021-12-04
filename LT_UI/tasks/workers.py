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
Implement your ASR worker interface in this function.
Please note that this functions is potentially called in parallel,
so if your workers rely on unique resources, you have to take care of synchronisation.

'source' is the content of the uploaded file.
'segmentation' is the content of the segmentation file.
'language' is one of the language codes specified in LANGUAGE_CHOICES.

Expects the result of the ASR process as (transcript, logging).
If there is any additional data/information, that you wish to pass to the mt processes, you can append them to the return tuple.
These will be passed as additional positional arguments to the mt worker function.

Example function body for experimental local setups without access to the actual workers:
    transcript = "0.34 4.32 Hello everyone in this room.\n4.78 6.03 Running is a great sport."
    return transcript, "random logs"
"""
def asr_worker(source: bytes, segmentation: str, language: str) -> 'tuple[str]':
    pass


"""
Implement your MT worker interface in this function.
Please note that this functions is potentially called in parallel,
so if your workers rely on unique resources, you have to take care of synchronisation.

'text' is the result of the ASR worker.
'language' is one of the language codes specified in LANGUAGE_CHOICES.
'translations' is a list of language codes specified in TRANSLATION_CHOICES.
'args' is a list of the additional data/information returned by the asr process

Expects the results of all MT processes returned as (language_code, translation, logging) tuples.
They can either be returned as a list or using 'yield' (a generator).

Example function body for experimental local setups without access to the actual workers:
    return [(code, f'translation_to_{code}', 'logging') for code in translations]
"""
def mt_worker(text: str, language: str, translations: 'list[str]', *args) -> 'list[tuple[str,str]]':
    pass
