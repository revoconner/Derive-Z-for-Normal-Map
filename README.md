# Normal Map Z Reconstruction v2.0
A simple Windows program to derive blue (Z) channel for normal maps with only Red and Green channels.

## Why is it needed? 
Most game engines will ignore the blue channel of a normal map and derive it during runtime, to save memory. So many artists will use that third channel (blue) to pack other textures data. It works fine in the engine, but if you need to export it and use that texture in a DCC program it may not work as expected without the correct blue channel. 

This app let's you reconstruct the Blue channel from the existing Red and Green channel and allow you to save the reconstructed normal map with all three channels intact.

## How to use
![image](https://github.com/user-attachments/assets/c89ceddc-afa5-418e-8c29-7fb112799d9e)
![image](https://github.com/user-attachments/assets/dc0c1e2a-6bbe-46d6-b0d9-3fbf10cc0f3b)



1. Download (from the releases) and run the **Normal Map Z Reconstruction.exe**
2. Select an image file using the "browse" button. You will see a preview on the left side if the image is supported.
3. Click the "Process" button to reconstruct the normal map. You will see a preivew on the right side if things go okay.
4. Click "Save As" button to save the image as jpg, png or tga with the filename and location you want.
5. Selecting more than one image file will make the program behave in batch processing mode, previews will be unavailable.
6. In batch processing mode the images will be saved with a suffix_processed in the file format you select during save as type. Don't type anything in the filename section, doing so may result in the files being saved without an extension.


## Supported formats
1. Jpeg
2. png
3. tga (targa)

## Changelog
**v1.0**
1. Initial commit

**v2.0**
1. Added batch processing mode.
2. Added alternate algorithm for linearsRGB images such as from vface (texturing.xyz)
3. Bug Fix - Icon will now show in the main window
