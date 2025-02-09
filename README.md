# Podkastomat

🪛 A tool for automatically downloading and transcribing podcasts, with the option to translate them into English.

📚 Built for language learners.

Don't have any podcasts to listen to? [Try some of these](podcasts.md).

## Usage

To add a podcast:

```sh
./update-config add
```

This will ask you for the name, language code, and the RSS URL of the podcast, as well as whether you want the main process to automatically download the latest episode of this podcast when it runs.

To configure translating podcasts from a given language - in this example, German - into English (without this step, podcasts will be transcribed but not translated).

```sh
./update-config translate de
```

To process all configured podcasts

```sh
./process
```

To fetch and process the earliest 3 episodes of a particular podcast

```sh
./process 'some podcast' old 3
```

Online help for additional options is available via `./process --help`

Downloaded episodes, and generated transcripts and translations, will be stored in `podcasts/{language}/{podcast_name}`.
E.g.: `podcasts/de/mission_klima_-_lösungen_für_die_krise`

## Manual configuration

Feel free to edit the `config.json` file

## System Requirements

* Linux (but it probably works on other platforms 🤷)
* Python 3 (tested on 3.8.10)
* One or both of the following:
  * [Whisper](https://github.com/openai/whisper/) (supports transcripts and translations)
  * [Vosk](https://alphacephei.com/vosk/install#python-installation-from-pypi) (supports transcripts)
* [Mutagen](https://pypi.org/project/mutagen/)

## Notes

Whisper (used by default for transcriptions and translations) is quite slow and resource intensive.  
It may be worth running the `process` script overnight, e.g. as a cron job.

To read the transcript using [Vortmaro](https://vortmaro.org/), you can start a local server in Python by running:

```sh
python3 -m http.server
```

This will report what URL it is running on, e.g. `http://localhost:8000/`.

Open the URL in a web browser, and navigate to the HTML transcript of the relevant episode.
