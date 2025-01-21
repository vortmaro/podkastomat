import glob
import re
import lib.fetcher as fetcher
import os
import os.path

from dateutil import parser as dateparser

charsToRemove = re.compile('[^\w\-]*')
multipleUnderscores = re.compile('__+')
startingNumerals = re.compile(r'^#?([0-9]+)')

def addRef(podcast):
    podcast['ref'] = getRef(podcast['name'])
    podcast['dir'] = f"podcasts/{podcast['lang']}/{podcast['ref']}"

def getRef(name):
    ref = name.lower()
    ref = ref.replace(' ', '_')
    ref = charsToRemove.sub('', ref)
    ref = multipleUnderscores.sub('_', ref)
    return ref

def getExtension(fileName):
    urlAndParams = fileName.partition('?')
    parts = urlAndParams[0].split('.')
    return parts.pop()

def replaceExtension(fileName, newExtension):
    parts = fileName.split('.')
    parts.pop()
    return '.'.join(parts) + '.' + newExtension

def saveEpisode(podcast, episode):
    match = startingNumerals.match(episode['title'])
    if episode['episode']:
        # Episode (& possibly season) number encoded in the RSS
        epNum = episode['episode']
        openingRef = epNum.zfill(5)
        identifier = f"{epNum}"
        if episode['season']:
            seasonNum = episode['season']
            openingRef = 's' + seasonNum.zfill(3) + 'ep' + openingRef
            identifier += f" of season {seasonNum}"
        offset = 0
    elif match:
        # Episode number deduced from its title
        epNum = match.group(1)
        openingRef = epNum.zfill(5)
        offset = len(match.group(0))
        identifier = epNum
    elif "date" in episode:
        # Podcast (or part thereof) where episodes only have a name and date
        date = dateparser.parse(episode['date'])
        openingRef = date.strftime("%Y-%m-%d_%H%M")
        offset = 0
        identifier = date.strftime("from %d %b %Y at %H:%M")
    else:
        print(f"Unable to determine identifier for episode:\n{episode}")
        return
    filenamePattern = f"{podcast['dir']}/{openingRef}_*"
    extantFiles = glob.glob(filenamePattern)
    if len(extantFiles) == 0:
        # Download new file
        ext = getExtension(episode['url'])
        episodeName = openingRef + '_' + episode['title'][offset:]
        if episode['subtitle']:
            episodeName += ' - ' + episode['subtitle']
        episodeRef = getRef(episodeName)
        fileName = f"{episodeRef}.{ext}"
        print(f"Downloading episode {identifier} of {podcast['name']} as {fileName}")
        fetcher.download(episode['url'], f"{podcast['dir']}/{fileName}")
    else:
        print(f"Episode {identifier} of {podcast['name']} has been downloaded previously; skipping")

def findAudio():
    return glob.glob('podcasts/*/*/*.m[4p][a3]')

def getLangCode(audioFile):
    parts = audioFile.split('/')
    return parts[1]

def getTranscriptFilename(audioFile):
    return replaceExtension(audioFile, 'transcript.txt')

def hasTranscript(audioFile):
    transcriptFile = getTranscriptFilename(audioFile)
    return os.path.isfile(transcriptFile)

def getTranslationFilename(audioFile):
    return replaceExtension(audioFile, 'translation.txt')

def hasTranslation(audioFile):
    translationFile = getTranslationFilename(audioFile)
    return os.path.isfile(translationFile)

def generateFromAudio(audioFile, task):
    if task == 'transcribe':
        newExt = 'transcript.txt'
    else:
        task = 'translate'
        newExt = 'translation.txt'

    langCode = getLangCode(audioFile)
    fileParts = audioFile.split('/')
    fileName = fileParts.pop()
    dir = '/'.join(fileParts)
    os.chdir(dir)

    cmd = f"whisper {fileName} --model medium --language {langCode} --task {task} --output_format vtt --fp16 False"
    os.system(cmd)

    # rename transcript/translation file generated
    generatedFile = replaceExtension(fileName, 'vtt')
    newFileName = replaceExtension(fileName, newExt)
    os.rename(generatedFile, newFileName)
    os.chdir('../..')
