import glob
import re
import lib.fetcher as fetcher
import mutagen
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

def saveEpisode(podcast, episode, options):
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
        if options.verbose:
            print(f"Downloading episode {identifier} of {podcast['name']} as {fileName}")
        fetcher.download(episode['url'], f"{podcast['dir']}/{fileName}")
    elif options.verbose:
        print(f"Episode {identifier} of {podcast['name']} has been downloaded previously; skipping")

def findAudio():
    return glob.glob('podcasts/*/*/*.m[4p][a3]')

def getAudioLength(audioFile):
    audio = mutagen.File(audioFile)
    totalLength = audio.info.length
    hours = int(totalLength // 3600)
    totalLength -= 3600 * hours
    minutes = int(totalLength // 60)
    totalLength -= 60 * minutes
    seconds = int(totalLength)
    if hours == 0:
        return f"{minutes}:{seconds}"
    else:
        return f"{hours}:{minutes}:{seconds}"

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

def getHtmlFilename(audioFile):
    return replaceExtension(audioFile, 'transcript.html')

def hasHtml(audioFile):
    htmlFile = getHtmlFilename(audioFile)
    return os.path.isfile(htmlFile)

def generateFromAudio(audioFile, task, options):
    if task == 'transcribe':
        newExt = 'transcript.txt'
    else:
        task = 'translate'
        newExt = 'translation.txt'

    langCode = getLangCode(audioFile)
    fileParts = audioFile.split('/')
    fileName = fileParts.pop()
    newFileName = replaceExtension(fileName, newExt)
    dir = '/'.join(fileParts)
    os.chdir(dir)

    if options.tts == 'vosk' or langCode == 'eo':
        cmd = f"vosk-transcriber -i {fileName} -l {langCode} -t srt -o {newFileName}"
        os.system(cmd)
    else:
        cmd = f"{options.whisperPath} {fileName} --model medium --language {langCode} --task {task} --output_format srt --fp16 False"
        os.system(cmd)

        # rename transcript/translation file generated
        generatedFile = replaceExtension(fileName, 'srt')
        os.rename(generatedFile, newFileName)
    os.chdir('../../..')

def generateHtml(audioFilename, options):
    langCode = getLangCode(audioFilename)
    htmlFilename = getHtmlFilename(audioFilename)
    transcriptFilename = getTranscriptFilename(audioFilename)

    if options.verbose:
        print(f"Generating HTML transcript {htmlFilename}")

    transcriptFile = open(transcriptFilename, 'r')
    data = transcriptFile.read().replace('\r\n', '\n')
    transcriptFile.close()

    paragraphs = data.split('\n\n')
    html = f"<!DOCTYPE html><html lang=\"{langCode}\"><body>"
    if len(paragraphs) == 1:
        html += '<p>' + paragraphs[0].replace('\n', '<br>\n') + '</p>\n'
    else:
        for para in paragraphs:
            html += '<p>' + para + '</p>\n'
    html += '</body></html>'
    htmlFile = open(htmlFilename, 'w')
    htmlFile.write(html)
    htmlFile.close()
