import argparse

class Options:
    verbose = False
    loadFeed = True
    downloadEpisodes = True
    generate = True
    filter = None
    episodes = 'new'
    numEpisodes = 1
    tts = 'whisper'

def rewireHelp(original_help):
    def newHelp():
        original_help()
        print("")
        print("Examples:")
        print("./process --no-feed --skip-download")
        print("    Only process previously downloaded episodes (useful e.g. if Whisper ran out of memory, or a podcast wasn't configured to translate episodes)")
        print("./process --filter 'the few' --age old --episodes 3")
        print("    Download and process the first 3 episodes of 'The Few Who Do'")
    return newHelp

def read():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filter', help="If specified, only configured podcasts which match the filter will be processed. A filter of 'pieds sur' would match 'Les Pieds sur terre'")
    parser.add_argument('--age', choices=['new', 'old'], default='new', help="Fetch the newest or oldest episode(s) for the matching podcast(s)")
    parser.add_argument('--episodes', type=int, default=1, help="The number of episode(s) to fetch for the matching podcast(s); 1 by default")
    parser.add_argument("--skip-feed", action="store_true", help="Skip the initial step of downloading the RSS feeds")
    parser.add_argument("--no-feed", action="store_true", dest="skip_feed", help="As per --skip-feed")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading podcast episodes")
    parser.add_argument("--no-download", action="store_true", dest="skip_download", help="As per --skip-download")
    parser.add_argument("--skip-gen", action="store_true", help="Skip generating transcripts and translations of podcast episodes")
    parser.add_argument("--no-gen", action="store_true", dest="skip_gen", help="As per --skip-gen")
    parser.add_argument("--verbose", action="store_true", help="Output a detailed report of actions as they are being taken")
    parser.add_argument("--vosk", action="store_true", help="Use Vosk instead of Whisper to generate transcripts")
    old_help = parser.print_help
    parser.print_help = rewireHelp(old_help)
    args = parser.parse_args()
    opts = Options()
    opts.filter = args.filter
    opts.episodes = args.age
    opts.numEpisodes = args.episodes
    opts.loadFeed = not args.skip_feed
    opts.downloadEpisodes = not args.skip_download
    opts.generate = not args.skip_gen
    opts.verbose = args.verbose
    if args.vosk:
        opts.tts = 'vosk'
    return opts
