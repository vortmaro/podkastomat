import lib.fetcher as fetcher
import os.path
from xml.dom import minidom

namespaces = {'itunes': 'itunes.com'}

def fetch(podcast, loadFeed):
    podcast['feed'] = podcast['dir'] + "/rss.xml"
    if not os.path.isdir(podcast['dir']):
        os.makedirs(podcast['dir'])
    if loadFeed:
        print(f"Downloading RSS for podcast {podcast['name']}")
        fetcher.download(podcast['url'], podcast['feed'])

# Get the text value of a child name with a given name, if available
def extractField(node, childNodeName):
    children = node.getElementsByTagName(childNodeName)
    if children.length == 0:
        return ''
    return children[0].firstChild.data

def getEpisodes(podcast, episodesFrom, numEpisodes):
    print(f"Getting latest episode from {podcast['name']}")
    doc = minidom.parse(podcast['feed'])
    root = doc.getElementsByTagName('channel')[0]
    epNodes = root.getElementsByTagName('item')
    epNodeNum = 0
    totalEpisodes = epNodes.length
    if episodesFrom == 'old':
        epNodeNum = totalEpisodes - 1
    episodes = []
    for i in range (0, numEpisodes):
        epNode = epNodes.item(epNodeNum)
        episode = {
            'title': extractField(epNode, 'title'),
            'subtitle': '',
            'url': epNode.getElementsByTagName('enclosure')[0].getAttribute('url'),
            'season': extractField(epNode, 'itunes:season'),
            'episode': extractField(epNode, 'itunes:episode')
        }
        subtitle = extractField(epNode, 'itunes:subtitle')
        if len(episode['title']) + len(subtitle) < 150:
            episode['subtitle'] = subtitle
        pubDate = extractField(epNode, 'pubDate')
        if pubDate:
            episode['date'] = pubDate
        episodes.append(episode)
        if episodesFrom == 'old':
            epNodeNum -= 1
        else:
            epNodeNum += 1
        if epNodeNum == -1 or epNodeNum == totalEpisodes:
            break
    return episodes
