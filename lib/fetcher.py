import urllib.request

urllib.request.build_opener()

# Simple wrapper to spoof User-Agent when fetching remote files
def download(remoteUrl, localFilename):
    localFile = open(localFilename, 'b+w')
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Podkastomat/0.1.0')]
    remoteFile = opener.open(remoteUrl)
    localFile.write(remoteFile.read())





