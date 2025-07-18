# augustus-update-translations-tool

You can build the application yourself using Python 3.11 or newer, which is recommended since packaged PyQt6 is still a large .exe (the release 1.0 skips the software render fallback "opengl32sw.dll", but still weights almost 30MB).

INSTRUCTIONS:
1. Select the source translation file from augustus/src/translations/ directory (usually you should translate from english.c)
2. Select destination translation file from augustus/src/translations/ directory (your translation language)
3. Click 'Generate .txt (...)' to save a txt file with just the required keys
or
3. Select 'Translate with UI' to open a list of keys requiring translation
4. Translate keys and click 'OK' to append the translated keys to the selected destination C file
