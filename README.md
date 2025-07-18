# augustus-update-translations-tool
Simple translation tool to help isolate missing translation keys from selected Augustus translation .c file.
The application uses PyQt6 to provide interface for simple RegEx functions and faciliate FileDialogs, for translators who would prefer a GUI to contribute translation work. 
App's release is a one file .exe which bundles a lot of PyQt6 packages as well as Python 3.11 to ensure compatibility and portability.

**This application is not directly supported by the Augustus team and the Augustus team does not bare any responsibility for it.**

It's a separate tool built to give contributors unfamiliar with C methods an alternative way to contribute translations. You will still need to submit the resulting .c file with a PR to the official Augustus repository.

You can build the application yourself using Python 3.11 or newer, which is recommended since packaged PyQt6 is still a large .exe (the release 1.0 skips the software render fallback "opengl32sw.dll", but still weights almost 30MB).

INSTRUCTIONS:
1. Select the source translation file from augustus/src/translations/ directory (usually you should translate from english.c)
2. Select destination translation file from augustus/src/translations/ directory (your translation language)
![ss1]([image-url](https://github.com/Sephirex95/augustus-update-translations-tool/blob/main-master/screenshot1.png))
3. Click 'Generate .txt (...)' to save a txt file with just the required keys
or
3. Select 'Translate with UI' to open a list of keys requiring translation
4. Translate keys and click 'OK' to append the translated keys to the selected destination C file
