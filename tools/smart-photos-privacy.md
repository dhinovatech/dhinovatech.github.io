# Smart Photos — Privacy Policy

Effective: 2026-09-26 · Publisher: Dhinovatech (www.dhinovatech.com) · Contact: dhinovatech@gmail.com

> Owner: host this page at a public URL (for example www.dhinovatech.com/smartphotos/privacy) and enter that URL in
> Partner Center (Store Policy 10.5.1). The in-app summary is Settings → Privacy → "How privacy works".

**Short version: Smart Photos collects nothing. Your photos, videos and everything the app learns about them stay on
your PC.**

## What Smart Photos does with your photos
Smart Photos shows the photos and videos in the folders you choose and uses artificial intelligence (AI) that runs on
your own PC to make them searchable: it recognizes what is in a photo, groups similar faces so you can name people,
reads text in photos, and works out places and dates. All of this happens on your device.

The results are kept in the app's own data folder on your PC:
- an index database (dates, places, tags, text found in photos, the names you give people, albums, favorites and your
  corrections);
- small preview images (thumbnails);
- numeric descriptions of photos and faces used for search and face grouping. Face descriptions are encrypted with a
  key protected by Windows for your user account.

Smart Photos never modifies, moves or renames your original files. It deletes a file only when you ask it to, and then
it goes to the Recycle Bin.

## What leaves your PC
**Nothing about your photos.** No photo, video, thumbnail, face, name, place, text, tag or search you type is ever sent
anywhere by Smart Photos. There is no account, no advertising, no analytics, no telemetry and no crash upload.

Smart Photos connects to the internet only to:
- **Download its AI models** from Hugging Face (huggingface.co), after you agree during setup or in Settings. These
  requests contain only the file names of the models, like any download. You can instead import the models from a file.
- **Nothing else.** Every connection the app makes is listed in Settings → Privacy → Network log, and **Offline mode**
  blocks all of them.

Windows itself handles some traffic that is not part of Smart Photos: the Microsoft Store (licensing, the purchase
of Smart Photos Pro, ratings and updates — Windows checks the license even while Offline mode is on), the Microsoft Edge WebView2
runtime used to draw the offline map (started with its background networking turned off), and Windows components that
provide AI acceleration (downloaded only when you choose *Prepare accelerators*, and never in Offline mode). If your
photos are in a cloud-synced folder such as OneDrive and some are online-only, OneDrive downloads a file when Smart
Photos reads it to make a thumbnail, unless you turn that off in Settings → Library or turn on Offline mode. These follow
your Windows and OneDrive settings and Microsoft's privacy statement (https://privacy.microsoft.com). Windows Error
Reporting may send crash information to Microsoft if you allow it in Windows settings; Smart Photos adds nothing to it.

## Things you choose to send
- **Report a problem / Report a wrong AI result.** These open a draft in your own email app, addressed to
  dhinovatech@gmail.com. You can read and change it, and nothing is sent unless you send it. A report contains the app
  version, Windows version, language and what you write; an AI report also contains what you were looking at (for
  example, the search you typed and how the app understood it, or the photo's file type and camera model). Reports never
  contain photos, file names, folder paths or locations. We use reports only to fix problems and reply to you, and delete
  them when they are no longer needed.
- **Crash report.** If Smart Photos closed unexpectedly, the next start offers to open an email draft with the error
  details (with your user name, file names and folder paths removed). As with other reports, nothing is sent unless you
  send it, and you can choose *Don't ask again*.
- **Export diagnostics.** Saves a ZIP of recent app logs, with file paths removed, to a place you choose. It is sent
  only if you attach it to an email yourself.
- **Share / Copy / Export.** Photos you share or export go only where you send them.

## Backups
Once a week Smart Photos saves a small backup of your curation (people's names, face positions, albums, favorites and
corrections — no photos) to `Documents\Smart Photos Backups`, so your work survives reinstalling Windows. If your
Documents folder is synced by OneDrive, the backup goes to `Smart Photos Backups` in your user folder instead, so it
stays on this PC. If you choose a folder that OneDrive syncs, OneDrive will copy the backup to your OneDrive; Settings
tells you when this is the case and lets you choose another folder or turn backups off. A backup lists which items are
favorites, archived or hidden by their content fingerprints (not their names or paths), and the names you gave people;
keep it where only you can read it. The thumbnail cache can't be moved into a cloud-synced folder.

## Children
Smart Photos is a general-audience app. It does not collect personal information from anyone, including children.

## Your control
- Delete everything the AI learned: Settings → Privacy → Delete all AI data (faces separately under People).
- Remove a folder from the library: its index data is removed; your files are untouched.
- Uninstalling Smart Photos removes its data folder. Backups (in Documents, or in your user folder) stay until you delete them.

## Changes
If this policy changes, the new version will be posted at the same address with a new effective date. Because Smart
Photos collects no data, a change can never apply to data collected earlier.

## Contact
Dhinovatech — dhinovatech@gmail.com — www.dhinovatech.com
