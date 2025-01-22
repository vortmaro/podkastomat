import re
import sys

isNumber = re.compile('^[0-9]+$')

class Options:
    verbose = False
    loadFeed = True
    downloadEpisodes = True
    generate = True
    filter = None
    episodes = 'new'
    numEpisodes = 1

def outputHelp():
    print("Usage: ./process [args] [filter [age] [episodes]]")
    print("")
    print("args:")
    print("--help")
    print("    Show this help information")
    print("--no-feed, --skip-feed")
    print("    Skip the initial step of downloading the RSS feeds")
    print("--no-download, --skip-download")
    print("    Skip downloading podcast episodes")
    print("--no-gen, --skip-gen")
    print("    Skip generating transcripts and translations of podcast episodes")
    print("")
    print("filter:")
    print("    If specified, only configured podcasts which match the filter will be processed")
    print("    A filter of 'pieds sur' would match 'Les Pieds sur terre'")
    print("")
    print("age:")
    print("    'new' (default), or 'old'")
    print("    Fetch the newest or oldest episode(s) for the matching podcast(s)")
    print("")
    print("episodes:")
    print("    1 by default")
    print("    The number of episode(s) to fetch for the matching podcast(s)")
    print("")
    print("Examples:")
    print("    ./process --help")
    print("    ./process --no-feed --skip-download")
    print("        Only process previously downloaded episodes (useful e.g. if Whisper ran out of memory,")
    print("        or a podcast wasn't configured to translate episodes)")
    print("    ./process 'the few' old 3")
    print("        Download and process the first 3 episodes of 'The Few Who Do'")

def read():
    opts = Options()
    for arg in sys.argv[1:]:
        if arg == 'help' or arg =='--help':
            outputHelp()
            sys.exit(0)
        elif arg == '--no-feed' or arg == '--skip-feed':
            opts.loadFeed = False
        elif arg == '--no-download' or arg == '--skip-download':
            opts.downloadEpisodes = False
        elif arg == "--no-gen" or arg == "--skip-gen":
            opts.generate = False
        elif arg == "--verbose":
            opts.verbose = True
        elif arg == 'new':
            opts.episodes = 'new'
        elif arg == 'old':
            opts.episodes = 'old'
        elif isNumber.match(arg):
            opts.numEpisodes = int(arg)
        elif opts.filter == None and arg[0:2] != '--':
            opts.filter = arg.lower()
        else:
            print(f"Unrecognised argument: {arg}")
            print("")
            outputHelp()
            sys.exit(1)
    return opts
