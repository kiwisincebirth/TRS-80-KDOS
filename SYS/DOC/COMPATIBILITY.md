# Compatibility

## Compatible Software

### Big Five Games

Appear to be able to save hiscores to disk.
Games that have a loader screen, also check for
existence of floppy disk and a patch needs to be installed to
bypass this

````
Search For : 
3A EC 37 CB 4F 20
Replace With :
3A EC 37 CB 4F 18

Search For :
3A EC 37 CB 4F C8
Replace With :
3A EC 37 CB 4F C9
````

### Visicalc

Appears to be able to load and save files to disk.

## Incompatible

### Infocom 

Tested and not working

### ZVM

Tested and not working

## FreHD solution

When running this on a FreHD there are several limitations
* Only provides a small sub set of functions (frehd limited firmware)
* Consumes 512 bytes more RAM for overlays (no paged ram)
* file management, and sub-Directories are not supported
* Many DOS API's (support File IO) are not supported
* Doesn't support Disk Basic extensions.
